"""
Email Service Implementation

Provides integration between API and email processing components
with proper error handling, validation, and comprehensive operations.

Design Considerations:
- Clean separation from route handling
- Comprehensive error handling
- Proper async/await usage
- Stateless service design
"""

import os
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any

from fastapi import Depends, HTTPException, status

from api.config import get_settings
from api.models.emails import (
    EmailSummary,
    EmailDetailResponse,
    EmailContent,
    EmailProcessingStats,
    EmailSettings,
    EmailAnalysisResponse,
    AnalysisMetadata,
    MeetingDetails
)

# Add directories to path to make imports work
import sys
import os

# Import core email processing components - mocked for now
class EmailProcessor:
    """Mocked Email Processor for API"""
    def __init__(self, gmail_client=None, llama_analyzer=None, deepseek_analyzer=None, response_categorizer=None, storage_path=None):
        self.gmail_client = gmail_client
        self.llama_analyzer = llama_analyzer
        self.deepseek_analyzer = deepseek_analyzer
        self.response_categorizer = response_categorizer
        self.storage_path = storage_path
        
    async def process_email_batch(self, batch_size):
        """Process a batch of emails"""
        # In a real implementation, this would process emails
        # Mock implementation just returns success counts
        return batch_size, 0, []

class LlamaAnalyzer:
    """Mocked Llama Analyzer for API"""
    async def classify_email(self, message_id, subject, content, sender):
        """Classify an email as meeting-related or not"""
        # Simple mock implementation
        is_meeting = "meet" in content.lower() or "meeting" in content.lower()
        return is_meeting, None

class DeepseekAnalyzer:
    """Mocked Deepseek Analyzer for API"""
    async def analyze_email(self, email_content):
        """Analyze email content for meeting details"""
        # Simple mock implementation
        if "meet" in email_content.lower() or "meeting" in email_content.lower():
            analysis_data = {
                "date": "tomorrow",
                "time": "2pm",
                "location": "Conference Room A",
                "agenda": "Project discussion",
                "participants": ["team"],
                "missing_elements": []
            }
            response_text = "I'll be there at 2pm tomorrow in Conference Room A."
            recommendation = "standard_response"
            return analysis_data, response_text, recommendation, None
        return None, None, "ignore", None

class ResponseCategorizer:
    """Mocked Response Categorizer for API"""
    pass

class GmailClient:
    """Mocked Gmail Client for API"""
    pass

class SecureStorage:
    """Mocked Secure Storage for API"""
    def __init__(self, storage_path):
        self.storage_path = storage_path
        
    async def get_processed_emails(self, limit, offset, category):
        """Get processed emails"""
        # Mock implementation
        return [], 0
        
    async def get_email_count(self, category):
        """Get count of emails in category"""
        # Mock implementation
        return 0
        
    async def get_email_by_id(self, message_id):
        """Get email by ID"""
        # Mock implementation
        return None

# Configure logging
logger = logging.getLogger(__name__)


class EmailService:
    """
    Comprehensive email processing service implementation.
    
    Provides integration between API routes and core email processing
    components with proper error handling and validation.
    """
    
    def __init__(self):
        """
        Initialize email service with required components.
        
        Sets up connections to email processing pipeline components
        with proper configuration and error handling.
        """
        self.settings = get_settings()
        
        # Load settings from storage or use defaults
        try:
            self.email_settings = self._load_settings()
        except Exception as e:
            logger.warning(f"Failed to load email settings: {str(e)}. Using defaults.")
            self.email_settings = EmailSettings()
        
        # Initialize storage
        self.storage = SecureStorage("data/secure")
        
        # Initialize core components
        try:
            self.gmail_client = GmailClient()
            self.llama_analyzer = LlamaAnalyzer()
            self.deepseek_analyzer = DeepseekAnalyzer()
            self.response_categorizer = ResponseCategorizer()
            
            # Initialize email processor with all components
            self.email_processor = EmailProcessor(
                gmail_client=self.gmail_client,
                llama_analyzer=self.llama_analyzer,
                deepseek_analyzer=self.deepseek_analyzer,
                response_categorizer=self.response_categorizer,
                storage_path="data/secure"
            )
            
            logger.info("Email service initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing email service: {str(e)}")
            raise RuntimeError(f"Failed to initialize email service: {str(e)}")
    
    async def get_emails(
        self,
        limit: int = 20,
        offset: int = 0,
        category: Optional[str] = None
    ) -> Tuple[List[EmailSummary], int]:
        """
        Retrieve processed emails with pagination and filtering.
        
        Implements efficient email retrieval with proper pagination,
        filtering, and error handling.
        
        Args:
            limit: Maximum emails to return
            offset: Number of emails to skip
            category: Optional category filter
            
        Returns:
            Tuple of (email list, total count)
            
        Raises:
            RuntimeError: If email retrieval fails
        """
        try:
            # Get emails from secure storage
            stored_emails = await self.storage.get_processed_emails(limit, offset, category)
            
            # Convert to API model format
            email_summaries = []
            for email in stored_emails:
                email_summaries.append(
                    EmailSummary(
                        message_id=email.get("message_id", "unknown"),
                        subject=email.get("subject", "No Subject"),
                        sender=email.get("sender", "unknown@example.com"),
                        received_at=email.get("received_at", datetime.utcnow()),
                        category=email.get("analysis_results", {}).get("final_category", "unknown"),
                        is_responded=email.get("responded", False)
                    )
                )
            
            # Get total count
            total_count = await self.storage.get_email_count(category)
            
            return email_summaries, total_count
            
        except Exception as e:
            logger.error(f"Error retrieving emails: {str(e)}")
            raise RuntimeError(f"Failed to retrieve emails: {str(e)}")
    
    async def get_email_by_id(self, message_id: str) -> Optional[EmailDetailResponse]:
        """
        Retrieve detailed email information by ID.
        
        Provides comprehensive email details with proper
        error handling and validation.
        
        Args:
            message_id: Email message ID
            
        Returns:
            Detailed email information or None if not found
            
        Raises:
            RuntimeError: If retrieval fails
        """
        try:
            # Get email from secure storage
            email_data = await self.storage.get_email_by_id(message_id)
            
            if not email_data:
                return None
                
            # Convert to API model format
            email_detail = EmailDetailResponse(
                message_id=email_data.get("message_id", "unknown"),
                subject=email_data.get("subject", "No Subject"),
                sender=email_data.get("sender", "unknown@example.com"),
                received_at=email_data.get("received_at", datetime.utcnow()),
                content=EmailContent(
                    raw_content=email_data.get("content", ""),
                    processed_content=email_data.get("processed_content", None),
                    html_content=email_data.get("html_content", None),
                    attachments=email_data.get("attachments", [])
                ),
                category=email_data.get("analysis_results", {}).get("final_category", "unknown"),
                is_responded=email_data.get("responded", False),
                analysis_results=email_data.get("analysis_results", None),
                processing_history=email_data.get("processing_history", [])
            )
            
            return email_detail
            
        except Exception as e:
            logger.error(f"Error retrieving email {message_id}: {str(e)}")
            raise RuntimeError(f"Failed to retrieve email: {str(e)}")
    
    async def analyze_email(
        self,
        content: str,
        subject: str,
        sender: str
    ) -> EmailAnalysisResponse:
        """
        Analyze email content using the processing pipeline.
        
        Implements comprehensive email analysis with proper error
        handling and integration with core analysis components.
        
        Args:
            content: Email content to analyze
            subject: Email subject
            sender: Email sender
            
        Returns:
            Analysis results with detailed information
            
        Raises:
            RuntimeError: If analysis fails
        """
        try:
            start_time = time.time()
            
            # Stage 1: Initial classification with LlamaAnalyzer
            is_meeting, llama_error = await self.llama_analyzer.classify_email(
                message_id="api_request",
                subject=subject,
                content=content,
                sender=sender
            )
            
            if llama_error:
                logger.error(f"Error in initial classification: {llama_error}")
                raise RuntimeError(f"Initial classification failed: {llama_error}")
            
            if not is_meeting:
                # Not meeting-related, return simple result
                end_time = time.time()
                processing_time = int((end_time - start_time) * 1000)
                
                return EmailAnalysisResponse(
                    is_meeting_related=False,
                    category="not_meeting",
                    recommended_action="ignore",
                    metadata=AnalysisMetadata(
                        model_version=self.settings.API_VERSION,
                        confidence_score=0.95,
                        processing_time_ms=processing_time
                    )
                )
            
            # Stage 2: Detailed analysis with DeepseekAnalyzer
            analysis_data, response_text, recommendation, deepseek_error = await self.deepseek_analyzer.analyze_email(
                email_content=content
            )
            
            if deepseek_error:
                logger.error(f"Error in detailed analysis: {deepseek_error}")
                raise RuntimeError(f"Detailed analysis failed: {deepseek_error}")
            
            # Extract meeting details if available
            meeting_details = None
            if analysis_data:
                missing_elements = analysis_data.get("missing_elements", "None")
                if isinstance(missing_elements, str):
                    missing_elements = [e.strip() for e in missing_elements.split(",") if e.strip() and e.lower() != "none"]
                
                meeting_details = MeetingDetails(
                    date=analysis_data.get("date"),
                    time=analysis_data.get("time"),
                    location=analysis_data.get("location"),
                    agenda=analysis_data.get("agenda"),
                    participants=analysis_data.get("participants"),
                    missing_elements=missing_elements
                )
            
            # Calculate processing time
            end_time = time.time()
            processing_time = int((end_time - start_time) * 1000)
            
            # Map recommendation to appropriate category and action
            category_mapping = {
                "standard_response": "meeting",
                "needs_review": "needs_review",
                "ignore": "not_actionable"
            }
            
            action_mapping = {
                "standard_response": "respond",
                "needs_review": "review",
                "ignore": "ignore"
            }
            
            category = category_mapping.get(recommendation, "unknown")
            action = action_mapping.get(recommendation, "review")
            
            # Build response
            response = EmailAnalysisResponse(
                is_meeting_related=True,
                category=category,
                recommended_action=action,
                meeting_details=meeting_details,
                suggested_response=response_text,
                metadata=AnalysisMetadata(
                    model_version=self.settings.API_VERSION,
                    confidence_score=0.85,  # Could extract from analysis_data if available
                    processing_time_ms=processing_time
                )
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error analyzing email: {str(e)}")
            raise RuntimeError(f"Failed to analyze email: {str(e)}")
    
    async def process_batch(self, batch_size: int = 50) -> Tuple[int, List[str]]:
        """
        Process a batch of unread emails.
        
        Triggers the email processing pipeline on unread emails
        with proper error handling and result tracking.
        
        Args:
            batch_size: Number of emails to process
            
        Returns:
            Tuple of (processed count, error messages)
            
        Raises:
            RuntimeError: If batch processing fails
        """
        try:
            # Process batch using email processor
            processed_count, error_count, error_messages = await self.email_processor.process_email_batch(batch_size)
            
            # Log results
            logger.info(f"Batch processing completed: {processed_count} processed, {error_count} errors")
            
            return processed_count, error_messages
            
        except Exception as e:
            logger.error(f"Error processing email batch: {str(e)}")
            raise RuntimeError(f"Failed to process email batch: {str(e)}")
    
    async def get_processing_stats(self) -> EmailProcessingStats:
        """
        Retrieve email processing statistics.
        
        Collects and formats comprehensive statistics about
        email processing operations with proper error handling.
        
        Returns:
            Email processing statistics
            
        Raises:
            RuntimeError: If statistics retrieval fails
        """
        try:
            # Get statistics from storage or calculate
            stats_file = "data/metrics/email_stats.json"
            
            if os.path.exists(stats_file):
                with open(stats_file, "r") as f:
                    stats_data = json.load(f)
                    
                return EmailProcessingStats(
                    total_emails_processed=stats_data.get("total_emails_processed", 0),
                    emails_by_category=stats_data.get("emails_by_category", {}),
                    average_processing_time_ms=stats_data.get("average_processing_time_ms", 0.0),
                    success_rate=stats_data.get("success_rate", 0.0),
                    stats_period_days=stats_data.get("stats_period_days", 30),
                    last_updated=datetime.fromisoformat(stats_data.get("last_updated", datetime.utcnow().isoformat()))
                )
            
            # Calculate stats if file doesn't exist
            total_processed = await self.storage.get_email_count(None)
            
            # Get emails by category
            categories = ["meeting", "needs_review", "not_actionable", "not_meeting"]
            emails_by_category = {}
            
            for category in categories:
                count = await self.storage.get_email_count(category)
                emails_by_category[category] = count
            
            # Default stats
            stats = EmailProcessingStats(
                total_emails_processed=total_processed,
                emails_by_category=emails_by_category,
                average_processing_time_ms=250.0,  # Default value
                success_rate=0.95,  # Default value
                stats_period_days=30,
                last_updated=datetime.utcnow()
            )
            
            # Save stats
            os.makedirs(os.path.dirname(stats_file), exist_ok=True)
            with open(stats_file, "w") as f:
                json.dump(
                    {
                        "total_emails_processed": stats.total_emails_processed,
                        "emails_by_category": stats.emails_by_category,
                        "average_processing_time_ms": stats.average_processing_time_ms,
                        "success_rate": stats.success_rate,
                        "stats_period_days": stats.stats_period_days,
                        "last_updated": stats.last_updated.isoformat()
                    },
                    f,
                    indent=2
                )
            
            return stats
            
        except Exception as e:
            logger.error(f"Error retrieving processing stats: {str(e)}")
            raise RuntimeError(f"Failed to retrieve processing statistics: {str(e)}")
    
    async def get_settings(self) -> EmailSettings:
        """
        Retrieve current email processing settings.
        
        Provides access to system configuration settings
        with proper error handling.
        
        Returns:
            Current email processing settings
            
        Raises:
            RuntimeError: If settings retrieval fails
        """
        try:
            return self.email_settings
        except Exception as e:
            logger.error(f"Error retrieving settings: {str(e)}")
            raise RuntimeError(f"Failed to retrieve settings: {str(e)}")
    
    async def update_settings(self, settings: EmailSettings) -> EmailSettings:
        """
        Update email processing settings.
        
        Applies and persists new configuration settings with
        proper validation and error handling.
        
        Args:
            settings: New email processing settings
            
        Returns:
            Updated email processing settings
            
        Raises:
            RuntimeError: If settings update fails
        """
        try:
            # Update settings
            self.email_settings = settings
            
            # Save settings to file
            settings_file = "data/config/email_settings.json"
            os.makedirs(os.path.dirname(settings_file), exist_ok=True)
            
            with open(settings_file, "w") as f:
                json.dump(settings.model_dump(), f, indent=2)
            
            logger.info("Email settings updated successfully")
            
            return settings
            
        except Exception as e:
            logger.error(f"Error updating settings: {str(e)}")
            raise RuntimeError(f"Failed to update settings: {str(e)}")
    
    def _load_settings(self) -> EmailSettings:
        """
        Load email settings from storage.
        
        Retrieves persisted settings with fallback to defaults
        and proper error handling.
        
        Returns:
            Email processing settings
            
        Raises:
            Exception: If settings loading fails
        """
        settings_file = "data/config/email_settings.json"
        
        if os.path.exists(settings_file):
            with open(settings_file, "r") as f:
                settings_data = json.load(f)
                return EmailSettings(**settings_data)
        
        # Return default settings if file doesn't exist
        return EmailSettings()
    
    def get_current_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        return datetime.utcnow().isoformat()


# Singleton instance for dependency injection
email_service = EmailService()

def get_email_service() -> EmailService:
    """Provide email service instance for dependency injection."""
    return email_service
