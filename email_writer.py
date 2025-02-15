from openai import OpenAI
import json
import base64
import re
import os
import logging
from email.mime.text import MIMEText
from datetime import datetime
from typing import Dict, Optional
from email_classifier import EmailMetadata
from gmail import GmailClient
from dotenv import load_dotenv

logger = logging.getLogger(__name__)
load_dotenv(override=True)

class EmailAgent:
    """Agent for processing and responding to emails."""
    
    def __init__(self):
        """Initialize the email agent."""
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.gmail = GmailClient()
        self.load_response_log()
        
    def load_response_log(self):
        """Load or create the response log that tracks all email responses."""
        try:
            with open('data/email_responses.json', 'r') as f:
                content = f.read().strip()
                if content:
                    self.response_log = json.load(f)
                else:
                    self.response_log = {"responses": []}
        except (FileNotFoundError, json.JSONDecodeError):
            self.response_log = {"responses": []}
            os.makedirs('data', exist_ok=True)
            with open('data/email_responses.json', 'w') as f:
                json.dump(self.response_log, f, indent=2)

    def save_response_log(self, email_id: str, response_data: Dict):
        """Save a new response to the log with timestamp."""
        self.response_log["responses"].append({
            "email_id": email_id,
            "response_time": datetime.now().isoformat(),
            "response_data": response_data
        })
        with open('data/email_responses.json', 'w') as f:
            json.dump(self.response_log, f, indent=2)

    def has_responded(self, email_id: str) -> bool:
        """Check if we've already responded to this email."""
        return any(r["email_id"] == email_id for r in self.response_log["responses"])

    def extract_meeting_info(self, content: str) -> Dict[str, Optional[str]]:
        """Extract meeting information from email content."""
        # Initialize with None values
        info = {
            'location': None,
            'agenda': None
        }
        
        # Location patterns
        location_patterns = [
            r'at\s+([^\.!?\n]+)',
            r'in\s+([^\.!?\n]+)',
            r'location:\s*([^\.!?\n]+)',
            r'meet\s+(?:at|in)\s+([^\.!?\n]+)'
        ]

        # Agenda patterns
        agenda_patterns = [
            r'(?:about|discuss|regarding|re:|topic:|agenda:)\s+([^\.!?\n]+)',
            r'for\s+([^\.!?\n]+\s+(?:meeting|discussion|sync|catch-up))',
            r'purpose:\s*([^\.!?\n]+)'
        ]

        # Extract location
        for pattern in location_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                info['location'] = match.group(1).strip()
                break

        # Extract agenda
        for pattern in agenda_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                info['agenda'] = match.group(1).strip()
                break

        return info

    def create_response(self, metadata: EmailMetadata) -> Optional[str]:
        """Create an appropriate response based on email metadata."""
        # Extract sender name from email
        sender_name = metadata.sender.split('<')[0].strip()
        if not sender_name:
            sender_name = metadata.sender
            
        # Extract meeting information
        meeting_info = self.extract_meeting_info(metadata.raw_content)
        
        # Check for missing information
        missing_info = {
            'location': not meeting_info['location'],
            'agenda': not meeting_info['agenda']
        }

        if any(missing_info.values()):
            # Create list of missing items
            missing_items = []
            if missing_info['location']:
                missing_items.append("the meeting location")
            if missing_info['agenda']:
                missing_items.append("the meeting agenda/purpose")

            # Join missing items with proper grammar
            if len(missing_items) > 1:
                missing_items[-1] = "and " + missing_items[-1]
            missing_info_text = ", ".join(missing_items) if len(missing_items) > 2 else " ".join(missing_items)

            return f"""Dear {sender_name},

Thank you for your meeting request. To help me properly schedule our meeting, could you please specify {missing_info_text}?

Best regards,
Ivaylo's AI Assistant"""

        # If we have all information, create confirmation
        return f"""Dear {sender_name},

Thank you for your meeting request. I am pleased to confirm our meeting at {meeting_info['location']} to discuss {meeting_info['agenda']}.

Best regards,
Ivaylo's AI Assistant"""

    def send_email(self, to_email: str, subject: str, message_text: str) -> bool:
        """Send an email using Gmail API."""
        message = MIMEText(message_text)
        message['to'] = to_email
        message['subject'] = subject

        # Encode the message
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')

        try:
            self.gmail.service.users().messages().send(
                userId="me",
                body={'raw': raw_message}
            ).execute()
            return True
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return False

    def process_email(self, metadata: EmailMetadata) -> bool:
        """
        Process an email and send appropriate response.
        This method is called by the EmailProcessor.
        """
        try:
            # Check if already responded
            if self.has_responded(metadata.message_id):
                logger.info(f"Already responded to email {metadata.message_id}")
                return True

            # Generate response
            response_text = self.create_response(metadata)
            if not response_text:
                logger.error("Failed to create response")
                return False

            # Prepare subject
            subject = metadata.subject if metadata.subject else "Meeting Request"
            subject_prefix = "Re: " if not subject.startswith("Re:") else ""
            full_subject = f"{subject_prefix}{subject}"

            # Send response
            success = self.send_email(
                to_email=metadata.sender,
                subject=full_subject,
                message_text=response_text
            )

            if success:
                # Log the response
                self.save_response_log(metadata.message_id, {
                    "sender": metadata.sender,
                    "subject": metadata.subject,
                    "response": response_text
                })
                return True

            return False

        except Exception as e:
            logger.error(f"Error processing email {metadata.message_id}: {e}")
            return False
