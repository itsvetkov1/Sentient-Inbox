import unittest
from datetime import datetime
from email_classifier import EmailClassifier, EmailRouter, EmailTopic, EmailMetadata

class MockMeetingAgent:
    """Mock agent for testing."""
    def __init__(self):
        self.processed_emails = []
        
    def process_email(self, metadata: EmailMetadata):
        self.processed_emails.append(metadata)

class TestEmailClassifier(unittest.TestCase):
    def setUp(self):
        self.classifier = EmailClassifier()
        
    def test_meeting_topic_detection(self):
        """Test detection of meeting-related emails."""
        test_cases = [
            {
                "subject": "Schedule a meeting next week",
                "content": "Let's discuss the project.",
                "expected_topic": EmailTopic.MEETING,
                "requires_response": True
            },
            {
                "subject": "Project Update",
                "content": "When are you free for a meeting?",
                "expected_topic": EmailTopic.MEETING,
                "requires_response": True
            },
            {
                "subject": "Let's sync up",
                "content": "Want to catch up on the project status?",
                "expected_topic": EmailTopic.MEETING,
                "requires_response": True
            },
            {
                "subject": "Quick chat?",
                "content": "Do you have time for a quick discussion?",
                "expected_topic": EmailTopic.MEETING,
                "requires_response": True
            },
            {
                "subject": "Available for a call?",
                "content": "Would like to discuss some ideas.",
                "expected_topic": EmailTopic.MEETING,
                "requires_response": True
            },
            {
                "subject": "Random subject",
                "content": "Random content",
                "expected_topic": EmailTopic.UNKNOWN,
                "requires_response": False
            }
        ]
        
        for case in test_cases:
            metadata = self.classifier.classify_email(
                message_id="test",
                subject=case["subject"],
                sender="test@example.com",
                content=case["content"],
                received_at=datetime.now()
            )
            self.assertEqual(metadata.topic, case["expected_topic"], 
                           f"Failed to detect meeting topic in: {case['subject']} - {case['content']}")
            self.assertEqual(metadata.requires_response, case["requires_response"],
                           f"Failed to detect response requirement in: {case['subject']} - {case['content']}")
            
    def test_response_required_detection(self):
        """Test detection of emails requiring response."""
        test_cases = [
            {
                "subject": "Question about project",
                "content": "Please let me know your thoughts.",
                "requires_response": True
            },
            {
                "subject": "Meeting tomorrow?",
                "content": "Can you attend?",
                "requires_response": True
            },
            {
                "subject": "FYI: Project update",
                "content": "Here's the latest status.",
                "requires_response": False
            }
        ]
        
        for case in test_cases:
            metadata = self.classifier.classify_email(
                message_id="test",
                subject=case["subject"],
                sender="test@example.com",
                content=case["content"],
                received_at=datetime.now()
            )
            self.assertEqual(metadata.requires_response, case["requires_response"])
            
    def test_error_handling(self):
        """Test error handling with invalid inputs."""
        # Test with None values
        metadata = self.classifier.classify_email(
            message_id="test",
            subject=None,
            sender="test@example.com",
            content=None,
            received_at=datetime.now()
        )
        self.assertEqual(metadata.topic, EmailTopic.UNKNOWN)
        self.assertFalse(metadata.requires_response)

class TestEmailRouter(unittest.TestCase):
    def setUp(self):
        self.router = EmailRouter()
        self.meeting_agent = MockMeetingAgent()
        self.router.register_agent(EmailTopic.MEETING, self.meeting_agent)
        
    def test_email_routing(self):
        """Test routing emails to appropriate agents."""
        # Test meeting email
        should_mark_read, error = self.router.process_email(
            message_id="test1",
            subject="Schedule a meeting",
            sender="test@example.com",
            content="Let's meet tomorrow. Please confirm.",
            received_at=datetime.now()
        )
        self.assertTrue(should_mark_read)
        self.assertIsNone(error)
        self.assertEqual(len(self.meeting_agent.processed_emails), 1)
        
        # Test unknown topic with no response needed
        should_mark_read, error = self.router.process_email(
            message_id="test2",
            subject="Random subject",
            sender="test@example.com",
            content="Random content",
            received_at=datetime.now()
        )
        self.assertFalse(should_mark_read)
        self.assertIsNone(error)  # No error since it just doesn't require response
        self.assertEqual(len(self.meeting_agent.processed_emails), 1)  # No change
        
        # Test unknown topic that needs response
        should_mark_read, error = self.router.process_email(
            message_id="test3",
            subject="Question",
            sender="test@example.com",
            content="Can you help me with this?",
            received_at=datetime.now()
        )
        self.assertFalse(should_mark_read)
        self.assertIsNotNone(error)  # Error since we need response but no agent available
        self.assertEqual(len(self.meeting_agent.processed_emails), 1)  # No change
        
    def test_no_response_needed(self):
        """Test handling emails not requiring response."""
        should_mark_read, error = self.router.process_email(
            message_id="test3",
            subject="FYI: Meeting cancelled",
            sender="test@example.com",
            content="The meeting has been cancelled.",
            received_at=datetime.now()
        )
        self.assertFalse(should_mark_read)
        self.assertIsNone(error)
        self.assertEqual(len(self.meeting_agent.processed_emails), 0)
        
    def test_error_handling(self):
        """Test error handling in router."""
        # Test with missing agent
        router = EmailRouter()  # No agents registered
        should_mark_read, error = router.process_email(
            message_id="test4",
            subject="Schedule meeting",
            sender="test@example.com",
            content="Let's meet. Please confirm.",
            received_at=datetime.now()
        )
        self.assertFalse(should_mark_read)
        self.assertIsNotNone(error)
        self.assertTrue("No agent available" in error)

if __name__ == '__main__':
    unittest.main()
