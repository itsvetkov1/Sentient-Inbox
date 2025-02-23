"""
Core email processing implementation with enhanced date handling
"""

from typing import Dict, List, Optional, Tuple
import logging
import asyncio
from datetime import datetime, timezone, timedelta
from pathlib import Path

from email_classifier import EmailRouter, EmailTopic, EmailMetadata
from processors.content_processor import ContentPreprocessor, EmailDateService
from secure_storage import SecureStorage
from gmail import GmailClient
from analyzers.llama_analyzer import LlamaAnalyzer
from deepseek_analyzer import DeepseekAnalyzer
from email_writer import EmailAgent

logger = logging.getLogger(__name__)

class EmailProcessor:
    """
    Enhanced email processor with robust date handling and parsing
    """
    
    def __init__(self, 
                 gmail_client: GmailClient,
                 llama_analyzer: LlamaAnalyzer,
                 deepseek_analyzer: DeepseekAnalyzer,
                 storage_path: str = "data/secure",
                 strict_date_parsing: bool = True):
        self.gmail = gmail_client
        self.router = EmailRouter()
        self.llama_analyzer = llama_analyzer
        self.deepseek_analyzer = deepseek_analyzer
        self.storage = SecureStorage(storage_path)
        self.content_processor = ContentPreprocessor()
        self.strict_date_parsing = strict_date_parsing

        Path(storage_path).mkdir(parents=True, exist_ok=True)

    def register_agent(self, topic: EmailTopic, agent: EmailAgent):
        """
        Register email agent for specific topic
        """
        self.router.register_agent(topic, agent)
        logger.info(f"Registered agent for topic: {topic}")
        
    async def process_email_batch(self, batch_size: int = 100) -> Tuple[int, int, List[str]]:
        """
        Process email batch with comprehensive date validation
        """
        processed_count = 0
        error_count = 0
        error_messages = []
        
        try:
            unread_emails = await asyncio.to_thread(
                self.gmail.get_unread_emails,
                max_results=batch_size
            )
            logger.info(f"Found {len(unread_emails)} unread emails")
            
            one_week_ago = datetime.now(timezone.utc) - timedelta(days=7)
            
            for email in unread_emails:
                message_id = email.get("message_id")
                try:
                    # Enhanced date parsing and validation
                    received_str = email.get("received_at", "")
                    received_date, parse_success = EmailDateService.parse_email_date(received_str)
                    
                    if not parse_success:
                        error_msg = f"Invalid date format for {message_id}: {received_str}"
                        logger.warning(error_msg)
                        error_count += 1
                        error_messages.append(error_msg)
                        continue
                        
                    # Store validated ISO date
                    email["received_at"] = EmailDateService.format_iso(received_date)
                    
                    # Check date threshold
                    if received_date < one_week_ago:
                        logger.info(f"Email {message_id} is older than a week, skipping")
                        continue
                        
                    # Check processing status
                    is_processed, check_success = await self.storage.is_processed(message_id)
                    if not check_success:
                        error_msg = f"Status check failed for {message_id}"
                        logger.error(error_msg)
                        error_count += 1
                        error_messages.append(error_msg)
                        continue
                        
                    if is_processed:
                        logger.info(f"Email {message_id} already processed, skipping")
                        continue
                        
                    # Process content
                    try:
                        processed_content = self.content_processor.preprocess_content(
                            email.get("content", "")
                        )
                        email["processed_content"] = processed_content.content
                    except Exception as e:
                        error_msg = f"Content processing failed for {message_id}: {e}"
                        logger.error(error_msg)
                        error_count += 1
                        error_messages.append(error_msg)
                        continue
                        
                    # Process through pipeline
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
                    
            logger.info(f"Processed {processed_count} emails with {error_count} errors")
            return processed_count, error_count, error_messages
            
        except Exception as e:
            error_msg = f"Error fetching unread emails: {e}"
            logger.error(error_msg)
            return 0, 1, [error_msg]

    async def _process_single_email(self, email: Dict) -> Tuple[bool, Optional[str]]:
        """
        Process single email with date-validated metadata
        """
        message_id = email.get("message_id")
        try:
            # Create validated metadata
            metadata = EmailMetadata(
                message_id=message_id,
                subject=email.get("subject", ""),
                sender=email.get("sender", ""),
                received_at=datetime.fromisoformat(email["received_at"]),
                topic=EmailTopic.MEETING,
                requires_response=False,
                raw_content=email.get("content", ""),
                analysis_data={}
            )
            
            # Stage 1: Initial Classification
            initial_result = await self.llama_analyzer.classify_email(
                message_id=message_id,
                subject=metadata.subject,
                content=email["processed_content"],
                sender=metadata.sender,
                email_type=EmailTopic.MEETING
            )
            
            if initial_result[0] == "meeting_related":
                # Stage 2: Detailed Analysis
                deepseek_result = await self.deepseek_analyzer.analyze_email(
                    email_content=email["processed_content"]
                )
                
                # Stage 3: Final Decision
                final_result = await self.llama_analyzer.make_decision(
                    initial_classification=initial_result[0],
                    deepseek_decision=deepseek_result[0],
                    analysis=deepseek_result[1]
                )
                
                # Update metadata with analysis results
                metadata = metadata._replace(
                    requires_response=final_result[0] == "standard_response",
                    analysis_data=final_result[1]
                )
                
                # Route email through processing pipeline
                success = await self.router.process_email(
                    message_id=message_id,
                    subject=metadata.subject,
                    sender=metadata.sender,
                    content=metadata.raw_content,
                    received_at=metadata.received_at
                )
                
                if success:
                    await self.storage.add_record(email)
                    return True, None
                return False, "Routing failed"
                
            else:
                logger.info(f"Email {message_id} classified as non-meeting")
                await self.storage.add_record(email)
                return True, None
                
        except Exception as e:
            error_msg = f"Pipeline error: {e}"
            logger.error(error_msg)
            return False, error_msg

    # Rest of the class remains unchanged