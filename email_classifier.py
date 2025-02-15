from typing import Dict, List, Optional, Tuple
from enum import Enum
import logging
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)

class EmailTopic(Enum):
    """Supported email topics for classification."""
    MEETING = "meeting"
    UNKNOWN = "unknown"
    # Add new topics here as more agents are introduced
    # Example: TASK = "task"
    # Example: REPORT = "report"

@dataclass
class EmailMetadata:
    """Metadata about a processed email."""
    message_id: str
    subject: str
    sender: str
    received_at: datetime
    topic: EmailTopic
    requires_response: bool
    raw_content: str

class EmailClassifier:
    """Classifies emails by topic and determines if they require a response."""
    
    def __init__(self):
        # Keywords and patterns for each topic
        self.topic_patterns: Dict[EmailTopic, List[str]] = {
            EmailTopic.MEETING: [
                "schedule meeting",
                "meeting request",
                "let's meet",
                "meet with",
                "meeting invitation",
                "calendar invite",
                "schedule time",
                "schedule a call",
                "set up a meeting",
                "arrange a meeting",
                "meeting schedule",
                "meeting availability",
                "when are you free",
                "your availability",
                "discuss",
                "sync",
                "catch up",
                "catch-up",
                "chat",
                "call",
                "meeting",
                "meet",
                "zoom",
                "teams",
                "google meet",
                "conference",
                "appointment",
                "schedule",
                "booking",
                "available",
                "availability",
                "time slot",
                "timeslot",
                "time to",
                "time for",
            ],
            # Add patterns for new topics as more agents are introduced
        }
        
        # Patterns indicating a response is required
        self.response_required_patterns = [
            "please respond",
            "let me know",
            "confirm",
            "rsvp",
            "your thoughts",
            "what do you think",
            "get back to me",
            "respond by",
            "need your input",
            "your feedback",
            "your response",
            "please reply",
            "awaiting your response",
            "available",
            "availability",
            "can you",
            "would you",
            "are you",
            "do you",
            "when",
            "where",
            "how about",
            "let's",
            "shall we",
            "want to",
            "would like to",
            "?",  # Questions usually require responses
        ]

    def _normalize_text(self, text: Optional[str]) -> str:
        """Normalize text for pattern matching."""
        if text is None:
            return ""
        return text.lower().strip()

    def _contains_pattern(self, text: str, patterns: List[str]) -> bool:
        """Check if text contains any of the patterns."""
        normalized_text = self._normalize_text(text)
        return any(pattern in normalized_text for pattern in patterns)

    def _determine_topic(self, subject: str, content: str) -> EmailTopic:
        """Determine the topic of an email based on its subject and content."""
        normalized_subject = self._normalize_text(subject)
        normalized_content = self._normalize_text(content)
        
        # Check each topic's patterns
        for topic, patterns in self.topic_patterns.items():
            # Check subject first as it's more reliable
            if self._contains_pattern(normalized_subject, patterns):
                return topic
            # Check content if subject didn't match
            if self._contains_pattern(normalized_content, patterns):
                return topic
        
        return EmailTopic.UNKNOWN

    def _requires_response(self, subject: str, content: str) -> bool:
        """Determine if an email requires a response."""
        normalized_text = f"{self._normalize_text(subject)} {self._normalize_text(content)}"
        return self._contains_pattern(normalized_text, self.response_required_patterns)

    def classify_email(self, 
                      message_id: str,
                      subject: str,
                      sender: str,
                      content: str,
                      received_at: datetime) -> EmailMetadata:
        """
        Classify an email and determine if it requires a response.
        
        Args:
            message_id: Unique identifier for the email
            subject: Email subject line
            sender: Email sender address
            content: Email body content
            received_at: When the email was received
            
        Returns:
            EmailMetadata containing classification results
        """
        try:
            topic = self._determine_topic(subject, content)
            requires_response = self._requires_response(subject, content)
            
            metadata = EmailMetadata(
                message_id=message_id,
                subject=subject,
                sender=sender,
                received_at=received_at,
                topic=topic,
                requires_response=requires_response,
                raw_content=content
            )
            
            logger.info(f"Classified email {message_id}: topic={topic.value}, requires_response={requires_response}")
            return metadata
            
        except Exception as e:
            logger.error(f"Error classifying email {message_id}: {e}")
            # Return as unknown topic that doesn't require response
            return EmailMetadata(
                message_id=message_id,
                subject=subject,
                sender=sender,
                received_at=received_at,
                topic=EmailTopic.UNKNOWN,
                requires_response=False,
                raw_content=content
            )

class EmailRouter:
    """Routes classified emails to appropriate agents."""
    
    def __init__(self):
        self.classifier = EmailClassifier()
        self.agents: Dict[EmailTopic, object] = {}
        
    def register_agent(self, topic: EmailTopic, agent: object):
        """Register an agent to handle a specific email topic."""
        self.agents[topic] = agent
        logger.info(f"Registered agent for topic: {topic.value}")
        
    def process_email(self,
                     message_id: str,
                     subject: str,
                     sender: str,
                     content: str,
                     received_at: datetime) -> Tuple[bool, Optional[str]]:
        """
        Process an email by classifying it and routing to appropriate agent.
        
        Args:
            message_id: Unique identifier for the email
            subject: Email subject line
            sender: Email sender address
            content: Email body content
            received_at: When the email was received
            
        Returns:
            Tuple of (should_mark_read: bool, error_message: Optional[str])
        """
        try:
            # Classify the email
            metadata = self.classifier.classify_email(
                message_id=message_id,
                subject=subject,
                sender=sender,
                content=content,
                received_at=received_at
            )
            
            # If no response required, keep unread
            if not metadata.requires_response:
                logger.info(f"Email {message_id} does not require response, keeping unread")
                return False, None
                
            # Get the appropriate agent
            agent = self.agents.get(metadata.topic)
            if not agent:
                logger.warning(f"No agent registered for topic: {metadata.topic.value}")
                return False, f"No agent available for topic: {metadata.topic.value}"
                
            # Process with agent
            try:
                agent.process_email(metadata)
                logger.info(f"Successfully processed email {message_id} with {metadata.topic.value} agent")
                return True, None
            except Exception as e:
                error_msg = f"Agent error processing email {message_id}: {e}"
                logger.error(error_msg)
                return False, error_msg
                
        except Exception as e:
            error_msg = f"Error routing email {message_id}: {e}"
            logger.error(error_msg)
            return False, error_msg
