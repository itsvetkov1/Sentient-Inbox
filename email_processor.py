from typing import Dict, List, Optional, Tuple
import logging
import hashlib
from datetime import datetime
import asyncio
from email_classifier import EmailRouter, EmailClassifier, EmailTopic, EmailMetadata
from secure_storage import SecureStorageManager
from deepseek_analyzer import DeepseekAnalyzer
logger = logging.getLogger(__name__)

class EmailProcessor:
    """
    Processes unread emails and routes them to appropriate agents with enhanced analysis capabilities.
    Implements asynchronous processing with secure storage, thread awareness, and AI-powered analysis.
    """
    
    def __init__(self, gmail_client, llama_analyzer, deepseek_analyzer: DeepseekAnalyzer, storage_path: str = "data/secure"):
        """
        Initialize the email processor with required components and services.
        
        Args:
            gmail_client: Gmail API client instance
            llama_analyzer: LlamaAnalyzer instance for general analysis
            deepseek_analyzer: DeepseekAnalyzer instance for meeting-specific analysis
            storage_path: Base path for secure storage
        """
        self.gmail = gmail_client
        self.router = EmailRouter()
        self.classifier = EmailClassifier()
        self.storage = SecureStorageManager(storage_path)
        self.llama_analyzer = llama_analyzer
        self.deepseek_analyzer = deepseek_analyzer
        
    def register_agent(self, topic: EmailTopic, agent: object):
        """
        Register an agent to handle a specific email topic.
        
        Args:
            topic: Email topic category
            agent: Agent instance implementing process_email method
        """
        self.router.register_agent(topic, agent)
        logger.info(f"Registered agent for topic: {topic.value}")
        
    def _is_already_processed(self, message_id: str) -> Tuple[bool, bool]:
        """
        Check if an email has already been processed with secure verification.
        
        Args:
            message_id: Unique identifier for the email
            
        Returns:
            Tuple of (is_processed, success)
        """
        return self.storage.is_processed(message_id)
        
    def _mark_as_processed(self, email_data: Dict) -> bool:
        """
        Mark an email as processed in secure storage with metadata.
        
        Args:
            email_data: Complete email data dictionary
            
        Returns:
            Success status of storage operation
        """
        record_id, success = self.storage.add_record(email_data)
        if not success:
            logger.error(f"Error marking email {email_data.get('message_id')} as processed")
        return success

    async def _analyze_email_content(self, message_id: str, subject: str, content: str, sender: str, email_type: EmailTopic) -> Tuple[str, Dict]:
        """
        Perform detailed analysis of email content using AI-powered analyzer.
        
        Args:
            message_id: Unique email identifier
            subject: Email subject line
            content: Email body content
            sender: Email sender address
            email_type: Type of email (e.g., meeting, general)
            
        Returns:
            Tuple of (recommendation, analysis_metadata)
        """
        try:
            # Use llama-3.3-70b-versatile for initial analysis
            recommendation, analysis = await self.llama_analyzer.analyze_email(
                message_id=message_id,
                subject=subject,
                content=content,
                sender=sender,
                email_type=email_type
            )
            
            # If it's a meeting email, use DeepSeek for additional analysis
            if email_type == EmailTopic.MEETING:
                deepseek_decision, deepseek_analysis = await self.deepseek_analyzer.analyze_email(content)
                if deepseek_decision == "standard_response":
                    recommendation = "needs_standard_response"
                elif deepseek_decision == "flag_for_action":
                    recommendation = "needs_review"
                else:  # deepseek_decision == "ignore"
                    recommendation = "ignore"
                analysis.update(deepseek_analysis)
            
            logger.info(f"Analysis completed for {message_id} with recommendation: {recommendation}")
            return recommendation, analysis
        except Exception as e:
            logger.error(f"Error analyzing email {message_id}: {e}")
            return "needs_review", {}

    async def _update_email_status(self, message_id: str, mark_read: bool) -> bool:
        """
        Update email read/unread status asynchronously.
        
        Args:
            message_id: Email ID to update
            mark_read: Whether to mark as read (True) or unread (False)
        """
        try:
            if mark_read:
                await asyncio.to_thread(self.gmail.mark_as_read, message_id)
            else:
                await asyncio.to_thread(self.gmail.mark_as_unread, message_id)
            return True
        except Exception as e:
            logger.error(f"Error updating email status: {e}")
            return False

    async def _process_single_email(self, email: Dict) -> Tuple[bool, Optional[str]]:
        """
        Process a single email with enhanced analysis and error handling.
        
        Args:
            email: Email data dictionary
            
        Returns:
            Tuple of (success, error_message)
        """
        message_id = email.get("message_id")
        try:
            # Classify email
            metadata = await self.classifier.classify_email(
                message_id=message_id,
                subject=email.get("subject", ""),
                sender=email.get("sender", ""),
                content=email.get("content", ""),
                received_at=email.get("received_at", datetime.now())
            )
            email_type = metadata.topic
            
            # Perform AI-powered analysis
            recommendation, analysis = await self._analyze_email_content(
                message_id=message_id,
                subject=email.get("subject", ""),
                content=email.get("content", ""),
                sender=email.get("sender", ""),
                email_type=email_type
            )
            
            if recommendation == "needs_standard_response":
                should_mark_read, error = await self.router.process_email(
                    message_id=message_id,
                    subject=email.get("subject", ""),
                    sender=email.get("sender", ""),
                    content=email.get("content", ""),
                    received_at=email.get("received_at", datetime.now())
                )
                
                if error:
                    return False, error
                
                # Update email status based on processing result
                if should_mark_read:
                    if await self._update_email_status(message_id, mark_read=True):
                        if self._mark_as_processed(email):
                            return True, None
                        return False, f"Failed to mark {message_id} as processed"
                    return False, f"Failed to mark {message_id} as read"
                else:
                    await self._update_email_status(message_id, mark_read=False)
                    return True, None
            elif recommendation == "ignore":
                # Mark as read and processed for ignored emails
                if await self._update_email_status(message_id, mark_read=True):
                    if self._mark_as_processed(email):
                        return True, f"Email {message_id} ignored and marked as read"
                    return False, f"Failed to mark {message_id} as processed"
                return False, f"Failed to mark {message_id} as read"
            else:
                # Keep emails needing review unread
                await self._update_email_status(message_id, mark_read=False)
                return True, f"Email {message_id} marked for {recommendation}"
                
        except Exception as e:
            error_msg = f"Error processing email {message_id}: {e}"
            logger.error(error_msg)
            return False, error_msg

    async def process_unread_emails(self) -> Tuple[int, int, List[str]]:
        """
        Process all unread emails asynchronously with enhanced analysis.
        
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
                    # Verify processing status
                    is_processed, check_success = self._is_already_processed(message_id)
                    if not check_success:
                        error_count += 1
                        error_messages.append(f"Failed to verify status of {message_id}")
                        continue
                        
                    if is_processed:
                        logger.info(f"Email {message_id} already processed, skipping")
                        continue
                    
                    # Process email with enhanced analysis
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
