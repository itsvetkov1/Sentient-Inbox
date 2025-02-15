import unittest
from datetime import datetime
from unittest.mock import Mock, patch
from email_processor import EmailProcessor
from email_classifier import EmailTopic
from secure_storage import SecureStorageManager

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
        
        # Initialize processor
        self.processor = EmailProcessor(self.gmail_client, "test_secure")
        self.processor.register_agent(EmailTopic.MEETING, self.meeting_agent)
        
    def tearDown(self):
        # Clean up any test files
        import shutil
        import os
        if os.path.exists("test_secure"):
            shutil.rmtree("test_secure")
            
    def test_email_processing(self):
        """Test processing of different types of emails."""
        processed_count, error_count, errors = self.processor.process_unread_emails()
        
        # Verify counts
        self.assertEqual(processed_count, 3)  # All emails should be processed
        self.assertEqual(error_count, 0)  # No errors expected
        self.assertEqual(len(errors), 0)
        
        # Verify meeting email was routed correctly
        self.assertEqual(len(self.meeting_agent.processed_emails), 1)
        self.assertEqual(
            self.meeting_agent.processed_emails[0].message_id,
            "meeting1"
        )
        
        # Verify read/unread status
        self.assertIn("meeting1", self.gmail_client.marked_read)  # Requires response
        self.assertIn("meeting2", self.gmail_client.marked_unread)  # No response needed
        self.assertNotIn("unknown1", self.gmail_client.marked_read)  # Unknown topic
        
    def test_duplicate_processing(self):
        """Test handling of already processed emails."""
        # Process emails first time
        self.processor.process_unread_emails()
        initial_processed = len(self.meeting_agent.processed_emails)
        
        # Process same emails again
        processed_count, error_count, errors = self.processor.process_unread_emails()
        
        # Verify no duplicate processing
        self.assertEqual(len(self.meeting_agent.processed_emails), initial_processed)
        self.assertEqual(processed_count, 0)  # No new emails processed
        self.assertEqual(error_count, 0)
        
        # Test duplicate detection with similar email
        duplicate_email = self.test_emails[0].copy()
        duplicate_email["message_id"] = "different_id"  # Different ID but same content
        self.gmail_client.unread_emails = [duplicate_email]
        
        processed_count, error_count, errors = self.processor.process_unread_emails()
        
        # Should detect as duplicate despite different ID
        self.assertEqual(len(self.meeting_agent.processed_emails), initial_processed)
        self.assertEqual(processed_count, 0)
        
    def test_error_handling(self):
        """Test handling of various error conditions."""
        # Test with failing Gmail client
        failing_gmail = MockGmailClient()
        failing_gmail.get_unread_emails = Mock(side_effect=Exception("API Error"))
        
        processor = EmailProcessor(failing_gmail, "test_secure")
        processed_count, error_count, errors = processor.process_unread_emails()
        
        self.assertEqual(processed_count, 0)
        self.assertEqual(error_count, 1)
        self.assertEqual(len(errors), 1)
        self.assertTrue("API Error" in errors[0])
        
        # Test with failing agent
        failing_agent = Mock()
        failing_agent.process_email = Mock(side_effect=Exception("Agent Error"))
        
        self.processor.register_agent(EmailTopic.MEETING, failing_agent)
        processed_count, error_count, errors = self.processor.process_unread_emails()
        
        self.assertTrue(error_count > 0)
        self.assertTrue(any("Agent Error" in error for error in errors))
        
    def test_storage_integration(self):
        """Test integration with secure storage."""
        # Process emails
        self.processor.process_unread_emails()
        
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
