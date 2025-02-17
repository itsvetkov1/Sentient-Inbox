import pytest
from datetime import datetime
from email_classifier import EmailClassifier, EmailRouter, EmailTopic, EmailMetadata
import pytest_asyncio  # Add this import

class MockMeetingAgent:
    """Mock agent for testing."""
    def __init__(self):
        """Initialize with empty processed emails list."""
        self.processed_emails = []
        
    async def process_email(self, metadata: EmailMetadata):
        """Process email asynchronously for testing."""
        self.processed_emails.append(metadata)
        return True

class TestEmailClassifier:
    @pytest_asyncio.fixture(autouse=True)
    async def setup_classifier(self):
        """Initialize the classifier before each test.
        
        Using pytest_asyncio.fixture ensures proper async initialization.
        The autouse=True parameter makes this fixture run automatically for each test.
        """
        self.classifier = EmailClassifier()
        # Yield to allow the test to run
        yield
        # Any cleanup would go here

    @pytest.mark.asyncio
    async def test_meeting_topic_detection(self):
        """Test detection of meeting-related emails."""
        test_cases = [
            {
                "subject": "Schedule a meeting next week",
                "content": "Let's discuss the project.",
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
            metadata = await self.classifier.classify_email(
                message_id="test",
                subject=case["subject"],
                sender="test@example.com",
                content=case["content"],
                received_at=datetime.now()
            )
            assert metadata.topic == case["expected_topic"], \
                f"Failed to detect meeting topic in: {case['subject']} - {case['content']}"
            assert metadata.requires_response == case["requires_response"], \
                f"Failed to detect response requirement in: {case['subject']} - {case['content']}"

    @pytest.mark.asyncio
    async def test_response_required_detection(self):
        """Test detection of emails requiring response."""
        test_cases = [
            {
                "subject": "Question about project",
                "content": "Please let me know your thoughts.",
                "requires_response": True
            },
            {
                "subject": "FYI: Project update",
                "content": "Here's the latest status.",
                "requires_response": False
            }
        ]

        for case in test_cases:
            metadata = await self.classifier.classify_email(
                message_id="test",
                subject=case["subject"],
                sender="test@example.com",
                content=case["content"],
                received_at=datetime.now()
            )
            assert metadata.requires_response == case["requires_response"]

    @pytest.mark.asyncio
    async def test_error_handling(self):
        """Test error handling with invalid inputs."""
        metadata = await self.classifier.classify_email(
            message_id="test",
            subject=None,
            sender="test@example.com",
            content=None,
            received_at=datetime.now()
        )
        assert metadata.topic == EmailTopic.UNKNOWN
        assert not metadata.requires_response

class TestEmailRouter:
    @pytest_asyncio.fixture(autouse=True)
    async def setup_router(self):
        """Initialize the router and agent before each test.
        
        Using pytest_asyncio.fixture ensures proper async initialization.
        The autouse=True parameter makes this fixture run automatically for each test.
        """
        self.router = EmailRouter()
        self.meeting_agent = MockMeetingAgent()
        self.router.register_agent(EmailTopic.MEETING, self.meeting_agent)
        yield
        # Any cleanup would go here

    @pytest.mark.asyncio
    async def test_email_routing(self):
        """Test routing emails to appropriate agents."""
        # Test meeting email
        should_mark_read, error = await self.router.process_email(
            message_id="test1",
            subject="Schedule a meeting",
            sender="test@example.com",
            content="Let's meet tomorrow. Please confirm.",
            received_at=datetime.now()
        )
        assert should_mark_read
        assert error is None
        assert len(self.meeting_agent.processed_emails) == 1

    @pytest.mark.asyncio
    async def test_no_response_needed(self):
        """Test handling emails not requiring response."""
        should_mark_read, error = await self.router.process_email(
            message_id="test3",
            subject="FYI: Meeting cancelled",
            sender="test@example.com",
            content="The meeting has been cancelled.",
            received_at=datetime.now()
        )
        assert not should_mark_read
        assert error is None
        assert len(self.meeting_agent.processed_emails) == 0

    @pytest.mark.asyncio
    async def test_error_handling(self):
        """Test error handling in router."""
        # Create a new router without any agents registered
        router = EmailRouter()
        should_mark_read, error = await router.process_email(
            message_id="test4",
            subject="Schedule meeting",
            sender="test@example.com",
            content="Let's meet. Please confirm.",
            received_at=datetime.now()
        )
        assert not should_mark_read
        assert error is not None
        assert "No agent available" in error