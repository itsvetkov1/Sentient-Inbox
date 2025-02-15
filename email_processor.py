from typing import Dict, List, Optional, Tuple
import logging
import hashlib
from datetime import datetime
from email_classifier import EmailRouter, EmailTopic, EmailMetadata
from secure_storage import SecureStorageManager

logger = logging.getLogger(__name__)

class EmailProcessor:
    """Processes unread emails and routes them to appropriate agents."""
    
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
        
    def _update_email_status(self, message_id: str, mark_read: bool) -> bool:
        """Update the read/unread status of an email."""
        try:
            if mark_read:
                self.gmail.mark_as_read(message_id)
            else:
                self.gmail.mark_as_unread(message_id)
            return True
        except Exception as e:
            logger.error(f"Error updating email status: {e}")
            return False
            
    async def process_unread_emails(self) -> Tuple[int, int, List[str]]:
        """
        Process all unread emails.
        
        Returns:
            Tuple of (processed_count, error_count, error_messages)
        """
        processed_count = 0
        error_count = 0
        error_messages = []
        
        try:
            # Get unread emails
            unread_emails = self.gmail.get_unread_emails()
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
                        
                    # Check if any message in the thread is already processed
                    thread_id = email.get("thread_id", "")
                    thread_messages = email.get("thread_messages", [])
                    
                    # Check each message in thread
                    thread_processed = False
                    for thread_msg_id in thread_messages:
                        is_processed, check_success = self._is_already_processed(thread_msg_id)
                        if not check_success:
                            logger.error(f"Failed to check thread message {thread_msg_id}, skipping for safety")
                            error_count += 1
                            error_messages.append(f"Failed to verify thread message {thread_msg_id}")
                            thread_processed = True
                            break
                            
                        if is_processed:
                            logger.info(f"Found processed message {thread_msg_id} in thread {thread_id}, skipping")
                            thread_processed = True
                            break
                            
                    if thread_processed:
                        continue
                    
                    # Generate hash including thread and recipient information
                    recipients = sorted(email.get("recipients", []))  # Sort for consistent hash
                    message_hash = hashlib.sha256(
                        f"{email.get('subject', '')}{email.get('sender', '')}"
                        f"{','.join(recipients)}{thread_id}".encode()
                    ).hexdigest()
                    
                    # Check for duplicates by hash
                    data = self.storage._read_encrypted_data()
                    for record in data.get("records", []):
                        if record.get("message_hash") == message_hash:
                            logger.info(f"Found duplicate email with hash {message_hash}, skipping")
                            continue
                        
                        # Also check thread ID to prevent duplicate responses in a thread
                        record_thread_id = record.get("thread_id")
                        if record_thread_id and record_thread_id == thread_id:
                            logger.info(f"Found existing response in thread {thread_id}, skipping")
                            continue
                
                    # Store thread information in email data
                    email["thread_id"] = thread_id
                    email["thread_messages"] = thread_messages
                    
                    # Process the email if not already handled
                    should_mark_read, error = await self.router.process_email(
                        message_id=message_id,
                        subject=email.get("subject", ""),
                        sender=email.get("sender", ""),
                        content=email.get("content", ""),
                        received_at=email.get("received_at", datetime.now())
                    )
                    
                    if error:
                        logger.warning(f"Error processing email {message_id}: {error}")
                        error_count += 1
                        error_messages.append(error)
                        continue
                    
                    # Update email status based on processing result
                    if should_mark_read:
                        if self._update_email_status(message_id, mark_read=True):
                            # Only mark as processed if successfully marked as read
                            if self._mark_as_processed(email):
                                processed_count += 1
                            else:
                                error_count += 1
                                error_messages.append(f"Failed to mark {message_id} as processed")
                        else:
                            error_count += 1
                            error_messages.append(f"Failed to mark {message_id} as read")
                    else:
                        # Ensure email stays unread
                        self._update_email_status(message_id, mark_read=False)
                        processed_count += 1
                    
                except Exception as e:
                    logger.error(f"Error processing email {message_id}: {e}")
                    error_count += 1
                    error_messages.append(str(e))
                    
        except Exception as e:
            logger.error(f"Error fetching unread emails: {e}")
            error_count += 1
            error_messages.append(str(e))
            
        logger.info(f"Processed {processed_count} emails with {error_count} errors")
        return processed_count, error_count, error_messages
