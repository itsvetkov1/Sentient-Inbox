from typing import Dict, List, Optional, Tuple
import logging
import asyncio
from datetime import datetime, timedelta
from email_classifier import EmailRouter, EmailClassifier, EmailTopic, EmailMetadata
from secure_storage import SecureStorage
from deepseek_analyzer import DeepseekAnalyzer
from analyzers.llama_analyzer import LlamaAnalyzer

logger = logging.getLogger(__name__)

class EmailProcessor:
    """
    Processes emails using a three-stage analysis pipeline with batch processing and weekly rolling history.
    Implements asynchronous processing with secure storage, thread awareness, and AI-powered analysis.
    """
    
    def __init__(self, gmail_client, llama_analyzer: LlamaAnalyzer, deepseek_analyzer: DeepseekAnalyzer, secure_storage: SecureStorage):
        """
        Initialize the email processor with required components and services.
        
        Args:
            gmail_client: Gmail API client instance
            llama_analyzer: LlamaAnalyzer instance for initial classification and final decision
            deepseek_analyzer: DeepseekAnalyzer instance for detailed content analysis
            secure_storage: SecureStorage instance for encrypted data management
        """
        self.gmail = gmail_client
        self.router = EmailRouter()
        self.classifier = EmailClassifier()
        self.storage = secure_storage
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
        logger.debug(f"Registered agent for topic: {topic.value}")
        
    async def _is_already_processed(self, message_id: str) -> Tuple[bool, bool]:
        """
        Check if an email has already been processed with secure verification.
        
        Args:
            message_id: Unique identifier for the email
            
        Returns:
            Tuple of (is_processed, success)
        """
        return await self.storage.is_processed(message_id)
        
    async def _mark_as_processed(self, email_data: Dict) -> bool:
        """
        Mark an email as processed in secure storage with metadata.
        
        Args:
            email_data: Complete email data dictionary
            
        Returns:
            Success status of storage operation
        """
        record_id, success = await self.storage.add_record(email_data)
        if not success:
            logger.error(f"Error marking email {email_data.get('message_id')} as processed")
        return success

    async def _analyze_email_content(self, message_id: str, subject: str, content: str, sender: str, email_type: EmailTopic) -> Tuple[str, Dict]:
        """
        Perform three-stage analysis of email content using AI-powered analyzers.
        
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
            # Stage 1: Initial Classification (Llama)
            initial_classification, initial_analysis = await self.llama_analyzer.classify_email(
                message_id=message_id,
                subject=subject,
                content=content,
                sender=sender,
                email_type=email_type
            )
            
            # Stage 2: Detailed Content Analysis (Deepseek R1)
            if initial_classification == "meeting_related":
                deepseek_decision, deepseek_analysis = await self.deepseek_analyzer.analyze_email(content)
                analysis = {**initial_analysis, **deepseek_analysis}
            else:
                deepseek_decision = None
                analysis = initial_analysis
            
            # Stage 3: Final Decision Making (Llama)
            final_decision, final_analysis = await self.llama_analyzer.make_decision(
                initial_classification=initial_classification,
                deepseek_decision=deepseek_decision,
                analysis=analysis
            )
            
            logger.debug(f"Analysis completed for {message_id} with final decision: {final_decision}")
            return final_decision, final_analysis
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
        Process a single email with three-stage analysis and error handling.
        Implements a single retry with 3-second delay on failure.
        
        Args:
            email: Email data dictionary
            
        Returns:
            Tuple of (success, error_message)
        """
        message_id = email.get("message_id")
        max_retries = 1
        retry_delay = 3  # seconds

        for attempt in range(max_retries + 1):
            try:
                # Perform three-stage AI-powered analysis
                final_decision, analysis = await self._analyze_email_content(
                    message_id=message_id,
                    subject=email.get("subject", ""),
                    content=email.get("content", ""),
                    sender=email.get("sender", ""),
                    email_type=email.get("email_type", EmailTopic.GENERAL)
                )
                
                if final_decision == "standard_response":
                    should_mark_read, error = await self.router.process_email(
                        message_id=message_id,
                        subject=email.get("subject", ""),
                        sender=email.get("sender", ""),
                        content=email.get("content", ""),
                        received_at=email.get("received_at", datetime.now())
                    )
                    
                    if error:
                        raise Exception(error)
                    
                    # Update email status based on processing result
                    if should_mark_read:
                        if await self._update_email_status(message_id, mark_read=True):
                            if await self._mark_as_processed(email):
                                return True, None
                            raise Exception(f"Failed to mark {message_id} as processed")
                        raise Exception(f"Failed to mark {message_id} as read")
                    else:
                        await self._update_email_status(message_id, mark_read=False)
                        return True, None
                elif final_decision == "ignore":
                    # Mark as read and processed for ignored emails
                    if await self._update_email_status(message_id, mark_read=True):
                        if await self._mark_as_processed(email):
                            return True, f"Email {message_id} ignored and marked as read"
                        raise Exception(f"Failed to mark {message_id} as processed")
                    raise Exception(f"Failed to mark {message_id} as read")
                else:
                    # Keep emails needing review unread
                    await self._update_email_status(message_id, mark_read=False)
                    return True, f"Email {message_id} marked for {final_decision}"
                    
            except Exception as e:
                error_msg = f"Error processing email {message_id}: {e}"
                logger.error(error_msg)
                
                if attempt < max_retries:
                    logger.info(f"Retrying in {retry_delay} seconds... (Attempt {attempt + 1} of {max_retries + 1})")
                    await asyncio.sleep(retry_delay)
                else:
                    return False, error_msg

        # This line should never be reached, but we include it for completeness
        return False, f"Failed to process email {message_id} after all retry attempts"

    async def process_email_batch(self, batch_size: int = 100) -> Tuple[int, int, List[str]]:
        """
        Process a batch of unread emails asynchronously with three-stage analysis.
        
        Args:
            batch_size: Number of emails to process in this batch
        
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
            
            one_week_ago = datetime.now() - timedelta(days=7)
            
            for email in unread_emails[:batch_size]:
                message_id = email.get("message_id")
                
                try:
                    # Check if email is within the last week
                    received_at = email.get("received_at")
                    if isinstance(received_at, str):
                        received_at = datetime.fromisoformat(received_at)
                    if received_at < one_week_ago:
                        logger.info(f"Email {message_id} is older than a week, skipping")
                        continue
                    
                    # Verify processing status
                    is_processed, check_success = await self._is_already_processed(message_id)
                    if not check_success:
                        error_count += 1
                        error_messages.append(f"Failed to verify status of {message_id}")
                        continue
                        
                    if is_processed:
                        logger.info(f"Email {message_id} already processed, skipping")
                        continue
                    
                    # Process email with three-stage analysis
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
                    
                if processed_count + error_count >= batch_size:
                    break
                    
        except Exception as e:
            error_msg = f"Error fetching unread emails: {e}"
            logger.error(error_msg)
            error_count += 1
            error_messages.append(error_msg)
            
        logger.info(f"Processed {processed_count} emails with {error_count} errors in this batch")
        return processed_count, error_count, error_messages
