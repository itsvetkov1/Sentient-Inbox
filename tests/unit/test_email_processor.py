import unittest
from datetime import datetime
from unittest.mock import Mock, patch
from email_processor import EmailProcessor
from email_classifier import EmailTopic, EmailRouter
from secure_storage import SecureStorageManager
from deepseek_analyzer import DeepseekAnalyzer
from analyzers.llama_analyzer import LlamaAnalyzer

class MockGmailClient:
    """Mock Gmail client for testing."""
    def __init__(self, unread_emails=None):
        self.unread_emails = unread_emails or []
        self.marked_read = set()
        self.marked_unread = set()
        
    def get_unread_emails(self):
        return self.unread_emails
        
    def mark_as_read(self, message_id):
        self.marked_read.add(message_id)
        
    def mark_as_unread(self, message_id):
        self.marked_unread.add(message_id)

class MockMeetingAgent:
    """Mock meeting agent for testing."""
    def __init__(self):
        self.processed_emails = []
        
    def process_email(self, metadata):
        self.processed_emails.append(metadata)

class MockLlamaAnalyzer:
    """Mock LlamaAnalyzer for testing."""
    def __init__(self):
        self.analyzed_emails = []

    async def classify_email(self, message_id: str, subject: str, content: str, sender: str):
        self.analyzed_emails.append(content)
        if "meeting" in content.lower() or "urgent" in content.lower():
            return True, None  # Is a meeting email, no error
        else:
            return False, None  # Not a meeting email, no error

class MockDeepseekAnalyzer:
    """Mock DeepseekAnalyzer for testing."""
    def __init__(self):
        self.analyzed_emails = []

    async def analyze_email(self, email_content: str):
        self.analyzed_emails.append(email_content)
        if "meeting" in email_content.lower():
            analysis_data = {
                "summary": "This is a meeting email",
                "completeness": "4/4",
                "missing_elements": "None"
            }
            response_text = "Thank you for your meeting request. I am pleased to confirm our meeting."
            recommendation = "standard_response"
            error = None
        elif "urgent" in email_content.lower():
            analysis_data = {
                "summary": "This email requires immediate attention",
                "completeness": "2/4",
                "missing_elements": "Time, Location"
            }
            response_text = "Thank you for your urgent message. Our team will review it promptly."
            recommendation = "needs_review"
            error = None
        else:
            analysis_data = {
                "summary": "This email can be ignored",
                "completeness": "1/4",
                "missing_elements": "Time, Location, Agenda"
            }
            response_text = "Thank you for your information."
            recommendation = "ignore"
            error = None
        return analysis_data, response_text, recommendation, error

class MockResponseCategorizer:
    """Mock ResponseCategorizer for testing."""
    def __init__(self):
        self.categorized_emails = []

    async def categorize_email(
        self,
        analysis_data,
        response_text,
        deepseek_recommendation,
        deepseek_summary=None
    ):
        self.categorized_emails.append((analysis_data, response_text, deepseek_recommendation))
        
        # Return based on recommendation
        if deepseek_recommendation == "standard_response":
            return "standard_response", response_text
        elif deepseek_recommendation == "needs_review":
            return "needs_review", None
        else:  # ignore
            return "ignore", None

class TestEmailProcessor(unittest.TestCase):
    def setUp(self):
        # Create test emails
        self.test_emails = [
            {
                "message_id": "meeting1",
                "subject": "Schedule a meeting",
                "sender": "test1@example.com",
                "content": "Let's meet tomorrow. Please confirm.",
                "received_at": datetime.now()
            },
            {
                "message_id": "meeting2",
                "subject": "Project Update",
                "sender": "test2@example.com",
                "content": "FYI: Project is on track.",  # No response needed
                "received_at": datetime.now()
            },
            {
                "message_id": "unknown1",
                "subject": "Random subject",
                "sender": "test3@example.com",
                "content": "Random content",
                "received_at": datetime.now()
            }
        ]
        
        # Initialize mocks
        self.gmail_client = MockGmailClient(self.test_emails)
        self.meeting_agent = MockMeetingAgent()
        
        # Initialize mocks
        self.llama_analyzer = MockLlamaAnalyzer()
        self.deepseek_analyzer = MockDeepseekAnalyzer()
        self.response_categorizer = MockResponseCategorizer()
        
        # Initialize processor
        self.processor = EmailProcessor(
            gmail_client=self.gmail_client,
            llama_analyzer=self.llama_analyzer,
            deepseek_analyzer=self.deepseek_analyzer,
            response_categorizer=self.response_categorizer,
            storage_path="test_secure"
        )
        
    def tearDown(self):
        # Clean up any test files
        import shutil
        import os
        if os.path.exists("test_secure"):
            shutil.rmtree("test_secure")
            
    @patch.object(EmailRouter, 'classify_email')
    async def test_email_processing(self, mock_classify_email):
        """Test processing of different types of emails."""
        # Mock the classify_email method to return MEETING for all emails
        mock_classify_email.return_value = EmailTopic.MEETING

        processed_count, error_count, errors = await self.processor.process_email_batch()
        
        # Verify counts
        self.assertEqual(processed_count, 3)  # All emails should be processed
        self.assertEqual(error_count, 0)  # No errors expected
        self.assertEqual(len(errors), 0)
        
        # Verify all emails were analyzed by LlamaAnalyzer
        self.assertEqual(len(self.llama_analyzer.analyzed_emails), 3)
        
        # Verify meeting emails were analyzed by DeepseekAnalyzer
        self.assertEqual(len(self.deepseek_analyzer.analyzed_emails), 3)
        
        # Verify meeting email was routed correctly
        self.assertEqual(len(self.meeting_agent.processed_emails), 1)
        self.assertEqual(
            self.meeting_agent.processed_emails[0].message_id,
            "meeting1"
        )
        
        # Verify read/unread status
        self.assertIn("meeting1", self.gmail_client.marked_read)  # Requires response
        self.assertIn("meeting2", self.gmail_client.marked_unread)  # Needs review
        self.assertIn("unknown1", self.gmail_client.marked_read)  # Standard response
        
    @patch.object(EmailRouter, 'classify_email')
    async def test_duplicate_processing(self, mock_classify_email):
        """Test handling of already processed emails."""
        # Mock the classify_email method to return MEETING for all emails
        mock_classify_email.return_value = EmailTopic.MEETING

        # Process emails first time
        await self.processor.process_email_batch()
        initial_processed = len(self.meeting_agent.processed_emails)
        
        # Process same emails again
        processed_count, error_count, errors = await self.processor.process_email_batch()
        
        # Verify no duplicate processing
        self.assertEqual(len(self.meeting_agent.processed_emails), initial_processed)
        self.assertEqual(processed_count, 0)  # No new emails processed
        self.assertEqual(error_count, 0)
        
        # Test duplicate detection with similar email
        duplicate_email = self.test_emails[0].copy()
        duplicate_email["message_id"] = "different_id"  # Different ID but same content
        self.gmail_client.unread_emails = [duplicate_email]
        
        processed_count, error_count, errors = await self.processor.process_email_batch()
        
        # Should detect as duplicate despite different ID
        self.assertEqual(len(self.meeting_agent.processed_emails), initial_processed)
        self.assertEqual(processed_count, 0)
        
    @patch.object(EmailRouter, 'classify_email')
    async def test_error_handling(self, mock_classify_email):
        """Test handling of various error conditions."""
        # Mock the classify_email method to return MEETING for all emails
        mock_classify_email.return_value = EmailTopic.MEETING

        # Test with failing Gmail client
        failing_gmail = MockGmailClient()
        failing_gmail.get_unread_emails = Mock(side_effect=Exception("API Error"))
        
        processor = EmailProcessor(
            gmail_client=failing_gmail, 
            llama_analyzer=self.llama_analyzer, 
            deepseek_analyzer=self.deepseek_analyzer, 
            response_categorizer=self.response_categorizer,
            storage_path="test_secure"
        )
        processed_count, error_count, errors = await processor.process_email_batch()
        
        self.assertEqual(processed_count, 0)
        self.assertEqual(error_count, 1)
        self.assertEqual(len(errors), 1)
        self.assertTrue("API Error" in errors[0])
        
        # Test with failing agent
        failing_agent = Mock()
        failing_agent.process_email = Mock(side_effect=Exception("Agent Error"))
        
        self.processor.register_agent(EmailTopic.MEETING, failing_agent)
        processed_count, error_count, errors = await self.processor.process_email_batch()
        
        self.assertTrue(error_count > 0)
        self.assertTrue(any("Agent Error" in error for error in errors))
        
    @patch.object(EmailRouter, 'classify_email')
    async def test_storage_integration(self, mock_classify_email):
        """Test integration with secure storage."""
        # Mock the classify_email method to return MEETING for all emails
        mock_classify_email.return_value = EmailTopic.MEETING

        # Process emails
        await self.processor.process_email_batch()
        
        # Verify storage
        storage = SecureStorageManager("test_secure")
        
        # Check meeting email was stored
        is_processed, success = storage.is_processed("meeting1")
        self.assertTrue(success)
        self.assertTrue(is_processed)
        
        # Check FYI email was not stored (kept unread)
        is_processed, success = storage.is_processed("meeting2")
        self.assertTrue(success)
        self.assertFalse(is_processed)

if __name__ == '__main__':
    unittest.main()
