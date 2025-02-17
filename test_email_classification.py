import pytest
from pytest_asyncio import fixture
from datetime import datetime
from email_classifier import EmailClassifier, EmailTopic, EmailMetadata

class TestEmailTopicClassification:
    """Test suite for verifying email topic classification functionality."""

    @fixture(scope="function", autouse=True)
    async def setup_classifier(self):
        """Initialize EmailClassifier instance before each test.
        
        This fixture creates a fresh classifier for each test case.
        The scope="function" means each test gets its own instance.
        The autouse=True means it runs automatically for every test.
        """
        # Create a new classifier instance
        self.classifier = EmailClassifier()
        
        # Let the test run
        yield
        
        # Any cleanup would go here if needed

    @pytest.mark.asyncio
    async def test_meeting_topic_classification(self):
        """
        Tests the classification of meeting-related emails across different formats
        and writing styles.
        """
        # Test cases represent different ways people might write about meetings
        meeting_test_cases = [
            {
                "name": "explicit_meeting_request",
                "subject": "Team Meeting Next Week",
                "content": "Let's schedule a meeting to discuss the project.",
                "expected_topic": EmailTopic.MEETING,
                "description": "Direct meeting request with explicit scheduling language"
            },
            {
                "name": "informal_meeting_suggestion",
                "subject": "Quick sync?",
                "content": "Do you have time to catch up tomorrow?",
                "expected_topic": EmailTopic.MEETING,
                "description": "Informal meeting request using casual language"
            }
        ]

        # Test each meeting-related case
        for case in meeting_test_cases:
            # Process the test email
            metadata = await self.classifier.classify_email(
                message_id=f"test_{case['name']}",
                subject=case['subject'],
                sender="test@example.com",
                content=case['content'],
                received_at=datetime.now()
            )

            # Verify the classification
            assert metadata.topic == case['expected_topic'], \
                f"Failed to identify meeting topic in case '{case['name']}' - {case['description']}\n" \
                f"Subject: {case['subject']}\nContent: {case['content']}"

    @pytest.mark.asyncio
    async def test_non_meeting_classification(self):
        """
        Tests the classification of non-meeting emails to ensure the classifier
        doesn't incorrectly identify regular emails as meeting-related.
        """
        non_meeting_test_cases = [
            {
                "name": "status_update",
                "subject": "Project Status Update",
                "content": "Here's the weekly progress report for the project.",
                "expected_topic": EmailTopic.UNKNOWN,
                "description": "Regular status update email"
            }
        ]

        for case in non_meeting_test_cases:
            metadata = await self.classifier.classify_email(
                message_id=f"test_{case['name']}",
                subject=case['subject'],
                sender="test@example.com",
                content=case['content'],
                received_at=datetime.now()
            )

            assert metadata.topic == case['expected_topic'], \
                f"Incorrectly classified as meeting in case '{case['name']}' - {case['description']}\n" \
                f"Subject: {case['subject']}\nContent: {case['content']}"

    @pytest.mark.asyncio
    async def test_error_handling(self):
        """
        Tests the classifier's error handling capabilities by providing
        invalid or problematic inputs.
        """
        # Test with None values
        metadata = await self.classifier.classify_email(
            message_id="test_error",
            subject=None,
            sender="test@example.com",
            content=None,
            received_at=datetime.now()
        )
        
        # Verify safe default values are used
        assert metadata.topic == EmailTopic.UNKNOWN, \
            "Failed to handle None values gracefully"
        assert metadata.subject == "", \
            "Failed to handle None subject"
        assert metadata.raw_content == "", \
            "Failed to handle None content"