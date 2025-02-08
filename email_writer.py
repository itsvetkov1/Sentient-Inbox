from openai import OpenAI
import json
from gmail import SCOPES, build
from google.oauth2.credentials import Credentials
import base64
from email.mime.text import MIMEText
from dotenv import load_dotenv
import os
from datetime import datetime
import re  # Added for location extraction from email content

load_dotenv(override=True)


class EmailAgent:
    def __init__(self):
        # Initialize OpenAI client for potential future use with more complex responses
        self.client = OpenAI(
            api_key=os.getenv('OPENAI_API_KEY')
        )
        self.load_schedule()
        self.load_response_log()
        self.setup_gmail_service()

    def load_schedule(self):
        """Load or create the schedule JSON file that tracks all meetings"""
        try:
            with open('schedule.json', 'r') as f:
                content = f.read().strip()
                if content:  # Check if file has content
                    self.schedule = json.load(f)
                else:
                    self.schedule = {"meetings": []}
        except (FileNotFoundError, json.JSONDecodeError):
            self.schedule = {"meetings": []}
            # Create the file with default structure
            with open('schedule.json', 'w') as f:
                json.dump(self.schedule, f, indent=2)

    def load_response_log(self):
        """Load or create the response log that tracks all email responses"""
        try:
            with open('email_responses.json', 'r') as f:
                content = f.read().strip()
                if content:
                    self.response_log = json.load(f)
                else:
                    self.response_log = {"responses": []}
        except (FileNotFoundError, json.JSONDecodeError):
            self.response_log = {"responses": []}
            # Create the file with default structure
            with open('email_responses.json', 'w') as f:
                json.dump(self.response_log, f, indent=2)

    def save_response_log(self, email_id, response_data):
        """Save a new response to the log with timestamp"""
        self.response_log["responses"].append({
            "email_id": email_id,
            "response_time": datetime.now().isoformat(),
            "response_data": response_data
        })
        with open('email_responses.json', 'w') as f:
            json.dump(self.response_log, f, indent=2)

    def has_responded(self, email_id):
        """Check if we've already responded to this email"""
        return any(r["email_id"] == email_id for r in self.response_log["responses"])

    def setup_gmail_service(self):
        """Initialize the Gmail API service"""
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        self.service = build('gmail', 'v1', credentials=creds)

    def check_availability(self, date, time):
        """Check if the proposed time slot is available"""
        for meeting in self.schedule['meetings']:
            if meeting['date'] == date and meeting['time'] == time:
                return False
        return True

    def create_response(self, email_content, sender_name, proposed_date, proposed_time):
        """
        Creates a polite, semi-formal response to meeting requests.
        Handles missing information by asking specific questions.
        If request needs review, sends an acknowledgment message.
        """
        # Check if we have all required information
        has_date = proposed_date is not None and proposed_date.strip() != ''
        has_time = proposed_time is not None and proposed_time.strip() != ''

        # Extract location from email content using pattern matching
        location_match = re.search(r'at\s+([^\.!?\n]+)', email_content.lower())
        has_location = bool(location_match)
        location = location_match.group(1).strip() if has_location else None

        # If we're missing any required information, ask for it
        if not (has_date and has_time and has_location):
            missing_items = []
            if not has_date:
                missing_items.append("the preferred date")
            if not has_time:
                missing_items.append("the meeting time")
            if not has_location:
                missing_items.append("the meeting location")

            missing_info = " and ".join(missing_items)

            return f"""Dear {sender_name},

Thank you for your meeting request. Could you please specify {missing_info}? This will help me properly schedule our meeting.

Best regards,
Ivaylo's AI Assistant"""

        # If we have all information but need to check availability
        if not self.check_availability(proposed_date, proposed_time):
            return f"""Dear {sender_name},

Thank you for your meeting request. I will review your proposed meeting time ({proposed_date} at {proposed_time}) and get back to you within 24 hours.

Best regards,
Ivaylo's AI Assistant"""

        # If we have all information and the time slot is available
        return f"""Dear {sender_name},

Thank you for your meeting request. I am pleased to confirm our meeting on {proposed_date} at {proposed_time} at {location}.

Best regards,
Ivaylo's AI Assistant"""

    def send_email(self, to_email, subject, message_text):
        """Send an email using Gmail API"""
        message = MIMEText(message_text)
        message['to'] = to_email
        message['subject'] = subject

        # Encode the message
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')

        try:
            self.service.users().messages().send(
                userId="me",
                body={'raw': raw_message}
            ).execute()
            return True
        except Exception as e:
            print(f"Error sending email: {e}")
            return False

    def process_meeting_request(self, email_id, email_content, sender_info, subject, proposed_date, proposed_time):
        """Process a meeting request and send an appropriate response"""
        # Check if we've already responded to this email
        if self.has_responded(email_id):
            print(f"Already responded to email {email_id}")
            return False

        # Generate and send response
        response_text = self.create_response(
            email_content,
            sender_info['name'],
            proposed_date,
            proposed_time
        )

        # Send the response
        subject_prefix = "Re: " if not subject.startswith("Re:") else ""
        success = self.send_email(
            to_email=sender_info['email'],
            subject=f"{subject_prefix}{subject}",
            message_text=response_text
        )

        if success:
            # Log the response
            self.save_response_log(email_id, {
                "sender": sender_info,
                "subject": subject,
                "date": proposed_date,
                "time": proposed_time,
                "response": response_text
            })
            return True
        return False


def main():
    """Main function to process meeting requests"""
    # Initialize the agent
    agent = EmailAgent()

    # Process meetings from meeting_mails.json
    with open('meeting_mails.json', 'r') as f:
        meeting_data = json.load(f)

    for meeting in meeting_data["meetings"]:
        agent.process_meeting_request(
            email_id=f"{meeting['date']}_{meeting['time']}_{meeting['sender']['email']}",
            email_content=f"Meeting request for {meeting['topic']} at {meeting['location']}",
            sender_info=meeting['sender'],
            subject=meeting['topic'],
            proposed_date=meeting['date'],
            proposed_time=meeting['time']
        )


if __name__ == "__main__":
    main()