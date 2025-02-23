import unittest
import asyncio
from unittest.mock import Mock, patch
from datetime import datetime
from email_processor import EmailProcessor
from email_classifier import EmailMetadata, EmailTopic
from groq_integration.client_wrapper import EnhancedGroqClient
from gmail import GmailClient
from email_writer import EmailAgent

import pytest

@pytest.mark.asyncio
class TestEndToEnd(unittest.TestCase):
    """End-to-end tests for the complete email processing pipeline."""

    @patch('email_classifier.EnhancedGroqClient')
    @patch('email_writer.EmailAgent')
    def setUp(self, mock_email_agent, mock_groq_client):
        """Set up test environment."""
        self.gmail_client = Mock(spec=GmailClient)
        self.groq_client = mock_groq_client.return_value
        self.email_agent = mock_email_agent.return_value
        self.email_processor = EmailProcessor(gmail_client=self.gmail_client)
        
        # Sample test email
        self.test_email = EmailMetadata(
            message_id="test_123",
            sender="test@example.com",
            subject="Project Meeting Request",
            raw_content="""
            Hi team,
            
            I'd like to schedule a meeting to discuss the new feature implementation.
            Let's meet at the virtual conference room at 2 PM tomorrow.
            
            The agenda includes:
            1. Feature requirements review
            2. Timeline discussion
            3. Resource allocation
            
            Best regards,
            Test User
            """,
            received_at=datetime.now(),
            topic=EmailTopic.MEETING,
            requires_response=True
        )

    @patch('gmail.GmailClient')
    @patch('groq_integration.client_wrapper.EnhancedGroqClient.process_with_retry')
    async def test_complete_email_processing(self, mock_groq, mock_gmail):
        """Test the complete email processing pipeline."""
        # Mock Groq response
        mock_groq.return_value = {
            "choices": [{
                "message": {
                    "content": "Dear Test User,\n\nThank you for your meeting request. I confirm the meeting at 2 PM tomorrow in the virtual conference room to discuss the new feature implementation, including requirements review, timeline, and resource allocation.\n\nBest regards,\nAI Assistant"
                }
            }]
        }

        # Mock Gmail send
        mock_gmail.return_value = True

        # Process email
        result = await self.email_processor.process_email(self.test_email)
        
        # Verify email was processed
        self.assertTrue(result, "Email processing failed")
        
        # Verify Groq was called with correct parameters
        mock_groq.assert_called_once()
        
        # Verify Gmail send was attempted
        mock_gmail.assert_called_once()

    @patch('gmail.GmailClient')
    async def test_meeting_detection(self, mock_gmail):
        """Test meeting detection and information extraction."""
        # Process email for meeting detection
        meeting_info = self.email_agent.extract_meeting_info(self.test_email.raw_content)
        
        # Verify meeting details were extracted
        self.assertEqual(meeting_info['location'], "virtual conference room")
        self.assertIn("feature implementation", meeting_info['agenda'])

    @patch('groq_integration.client_wrapper.EnhancedGroqClient.process_with_retry')
    async def test_response_generation(self, mock_groq):
        """Test AI response generation."""
        # Mock Groq response
        mock_response = {
            "choices": [{
                "message": {
                    "content": "Test response content"
                }
            }]
        }
        mock_groq.return_value = mock_response

        # Generate response
        response = await self.email_agent.create_response(self.test_email)
        
        # Verify response was generated
        self.assertIsNotNone(response)
        self.assertIn("Test response content", response)

    async def test_metrics_tracking(self):
        """Test performance metrics tracking."""
        # Process email to generate metrics
        await self.email_processor.process_email(self.test_email)
        
        # Get metrics
        metrics = self.groq_client.get_performance_metrics()
        
        # Verify metrics were recorded
        self.assertIsNotNone(metrics)
        self.assertIn('avg_response_time', metrics)
        self.assertIn('total_requests', metrics)
        self.assertIn('success_rate', metrics)

class AsyncioTestRunner:
    """Custom test runner for handling async tests."""
    
    def run_async_test(self, test_func):
        """Run an async test function."""
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(test_func())

    def run_test_case(self, test_case):
        """Run all tests in a test case."""
        for name in dir(test_case):
            if name.startswith('test_'):
                test_func = getattr(test_case, name)
                if asyncio.iscoroutinefunction(test_func):
                    self.run_async_test(test_func)

def run_tests():
    """Run all end-to-end tests."""
    runner = AsyncioTestRunner()
    test_case = TestEndToEnd()
    runner.run_test_case(test_case)

if __name__ == '__main__':
    run_tests()
