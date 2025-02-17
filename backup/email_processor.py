from typing import Dict, List, Optional, Tuple
import logging
import hashlib
from datetime import datetime
import asyncio
from email_classifier import EmailRouter, EmailTopic, EmailMetadata
from secure_storage import SecureStorageManager

logger = logging.getLogger(__name__)

class EmailProcessor:
    """
    Processes unread emails and routes them to appropriate agents.
    Implements asynchronous processing with secure storage and thread awareness.
    """
    
    def __init__(self, gmail_client, storage_path: str = "data/secure"):
        """
        Initialize the email processor.
        
        Args:
            gmail_client: Gmail API client instance
            storage_path: Path for secure storage
        """
        self.gmail = gmail_client
        self.router = EmailRouter()
        self.storage = SecureStorageManager(storage_path)
        
    def register_agent(self, topic: EmailTopic, agent: object):
        """Register an agent to handle a specific email topic."""
        self.router.register_agent(topic, agent)
        logger.info(f"Registered agent for topic: {topic.value}")
        
    def _is_already_processed(self, message_id: str) -> Tuple[bool, bool]:
        """
        Check if an email has already been processed.
        Returns: Tuple of (is_processed, success)
        """
        return self.storage.is_processed(message_id)
        
    def _mark_as_processed(self, email_data: Dict) -> bool:
        """Mark an email as processed in secure storage."""
        record_id, success = self.storage.add_record(email_data)
        if not success:
            logger.error(f"Error marking email {email_data.get('message_id')} as processed")
        return success
        
    async def _update_email_status(self, message_id: str, mark_read: bool) -> bool:
        """
        Update the read/unread status of an email asynchronously.
        
        Args:
            message_id: Email ID to update
            mark_read: Whether to mark as read (True) or unread (False)
        """
        try:
            # Execute Gmail API calls in a thread pool
            if mark_read:
                await asyncio.to_thread(self.gmail.mark_as_read, message_id)
            else:
                await asyncio.to_thread(self.gmail.mark_as_unread, message_id)
            return True
        except Exception as e:
            logger.error(f"Error updating email status: {e}")
            return False
            
    async def _check_thread_status(self, thread_messages: List[str]) -> Tuple[bool, List[str]]:
        """
        Check the processed status of all messages in a thread.
        
        Args:
            thread_messages: List of message IDs in the thread
            
        Returns:
            Tuple of (thread_processed, error_messages)
        """
        error_messages = []
        
        for thread_msg_id in thread_messages:
            is_processed, check_success = self._is_already_processed(thread_msg_id)
            if not check_success:
                error_msg = f"Failed to verify thread message {thread_msg_id}"
                logger.error(error_msg)
                error_messages.append(error_msg)
                return True, error_messages
                
            if is_processed:
                logger.info(f"Found processed message {thread_msg_id} in thread")
                return True, error_messages
                
        return False, error_messages

    async def _process_single_email(self, email: Dict) -> Tuple[bool, Optional[str]]:
        """
        Process a single email with error handling and status updates.
        
        Args:
            email: Email data dictionary
            
        Returns:
            Tuple of (success, error_message)
        """
        message_id = email.get("message_id")
        try:
            # Process with router
            should_mark_read, error = await self.router.process_email(
                message_id=message_id,
                subject=email.get("subject", ""),
                sender=email.get("sender", ""),
                content=email.get("content", ""),
                received_at=email.get("received_at", datetime.now())
            )
            
            if error:
                return False, error
            
            # Update email status
            if should_mark_read:
                if await self._update_email_status(message_id, mark_read=True):
                    if self._mark_as_processed(email):
                        return True, None
                    return False, f"Failed to mark {message_id} as processed"
                return False, f"Failed to mark {message_id} as read"
            else:
                await self._update_email_status(message_id, mark_read=False)
                return True, None
                
        except Exception as e:
            error_msg = f"Error processing email {message_id}: {e}"
            logger.error(error_msg)
            return False, error_msg

    async def process_unread_emails(self) -> Tuple[int, int, List[str]]:
        """
        Process all unread emails asynchronously.
        
        Returns:
            Tuple of (processed_count, error_count, error_messages)
        """
        processed_count = 0
        error_count = 0
        error_messages = []
        
        try:
            # Get unread emails
            unread_emails = await asyncio.to_thread(self.gmail.get_unread_emails)
            logger.info(f"Found {len(unread_emails)} unread emails")
            
            for email in unread_emails:
                message_id = email.get("message_id")
                
                try:
                    # Check if already processed
                    is_processed, check_success = self._is_already_processed(message_id)
                    if not check_success:
                        logger.error(f"Failed to check processed status for {message_id}, skipping for safety")
                        error_count += 1
                        error_messages.append(f"Failed to verify status of {message_id}")
                        continue
                        
                    if is_processed:
                        logger.info(f"Email {message_id} already processed, skipping")
                        continue
                        
                    # Check thread status
                    thread_id = email.get("thread_id", "")
                    thread_messages = email.get("thread_messages", [])
                    thread_processed, thread_errors = await self._check_thread_status(thread_messages)
                    
                    if thread_errors:
                        error_count += len(thread_errors)
                        error_messages.extend(thread_errors)
                        continue
                        
                    if thread_processed:
                        logger.info(f"Thread {thread_id} already processed, skipping")
                        continue
                    
                    # Check for duplicates
                    recipients = sorted(email.get("recipients", []))
                    message_hash = hashlib.sha256(
                        f"{email.get('subject', '')}{email.get('sender', '')}"
                        f"{','.join(recipients)}{thread_id}".encode()
                    ).hexdigest()
                    
                    data = self.storage._read_encrypted_data()
                    is_duplicate = False
                    
                    for record in data.get("records", []):
                        if record.get("message_hash") == message_hash:
                            logger.info(f"Found duplicate email with hash {message_hash}, skipping")
                            is_duplicate = True
                            break
                        
                        record_thread_id = record.get("thread_id")
                        if record_thread_id and record_thread_id == thread_id:
                            logger.info(f"Found existing response in thread {thread_id}, skipping")
                            is_duplicate = True
                            break
                            
                    if is_duplicate:
                        continue
                
                    # Store thread information
                    email["thread_id"] = thread_id
                    email["thread_messages"] = thread_messages
                    
                    # Process email
                    success, error = await self._process_single_email(email)
                    if success:
                        processed_count += 1
                    else:
                        error_count += 1
                        error_messages.append(error)
                    
                except Exception as e:
                    error_msg = f"Error processing email {message_id}: {e}"
                    logger.error(error_msg)
                    error_count += 1
                    error_messages.append(error_msg)
                    
        except Exception as e:
            error_msg = f"Error fetching unread emails: {e}"
            logger.error(error_msg)
            error_count += 1
            error_messages.append(error_msg)
            
        logger.info(f"Processed {processed_count} emails with {error_count} errors")
        return processed_count, error_count, error_messages