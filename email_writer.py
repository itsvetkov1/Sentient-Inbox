from openai import OpenAI
import json
from gmail import SCOPES, build
from google.oauth2.credentials import Credentials
import base64
from email.mime.text import MIMEText
from dotenv import load_dotenv
import os
from datetime import datetime
import re

load_dotenv(override=True)


class EmailAgent:
    def __init__(self):
        # Initialize OpenAI client for potential future use with more complex responses
        self.client = OpenAI(
            api_key=os.getenv('OPENAI_API_KEY')
        )
        # Initialize list of files that need cleanup after processing
        self.files_to_cleanup = [
            'emails.txt',
            'meeting_mails.json',
            'schedule.json'
        ]
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

    def cleanup_files(self):
        """
        Cleans up all temporary files after email processing to prevent duplicates.
        This includes resetting JSON files to their default state and clearing text files.
        """
        try:
            # Reset emails.txt to empty state
            with open('emails.txt', 'w', encoding='utf-8') as f:
                f.write('Number of unread emails: 0\n\n')

            # Reset meeting_mails.json to default state
            default_meeting_state = {
                "last_updated": datetime.now().isoformat(),
                "meetings": []
            }
            with open('meeting_mails.json', 'w') as f:
                json.dump(default_meeting_state, f, indent=2)

            # Reset schedule.json to default state while preserving structure
            default_schedule_state = {
                "meetings": []
            }
            with open('schedule.json', 'w') as f:
                json.dump(default_schedule_state, f, indent=2)

            # Update internal schedule state
            self.schedule = default_schedule_state

            return True
        except Exception as e:
            print(f"Error during file cleanup: {e}")
            return False

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
        Creates a response to meeting requests, checking for three essential elements:
        1. Time (date and time)
        2. Location/Place
        3. Agenda/Purpose
        """
        # Initialize dictionary to track missing information
        missing_info = {
            'time': not (proposed_time and proposed_time.strip()),
            'date': not (proposed_date and proposed_date.strip()),
            'location': True,  # Default to True, will update in check
            'agenda': True  # Default to True, will update in check
        }

        # Check for location using various common patterns
        location_patterns = [
            r'at\s+([^\.!?\n]+)',  # "at the office"
            r'in\s+([^\.!?\n]+)',  # "in the conference room"
            r'location:\s*([^\.!?\n]+)',  # "location: office"
            r'meet\s+(?:at|in)\s+([^\.!?\n]+)'  # "meet at Starbucks"
        ]

        for pattern in location_patterns:
            if re.search(pattern, email_content, re.IGNORECASE):
                missing_info['location'] = False
                break

        # Check for agenda/purpose using common patterns
        agenda_patterns = [
            r'(?:about|discuss|regarding|re:|topic:|agenda:)\s+([^\.!?\n]+)',  # "to discuss project status"
            r'for\s+([^\.!?\n]+\s+(?:meeting|discussion|sync|catch-up))',  # "for project status meeting"
            r'purpose:\s*([^\.!?\n]+)'  # "purpose: project review"
        ]

        for pattern in agenda_patterns:
            if re.search(pattern, email_content, re.IGNORECASE):
                missing_info['agenda'] = False
                break

        # If we're missing any information, create a response asking for all missing items
        if any(missing_info.values()):
            missing_items = []
            if missing_info['date']:
                missing_items.append("the preferred date")
            if missing_info['time']:
                missing_items.append("the meeting time")
            if missing_info['location']:
                missing_items.append("the meeting location")
            if missing_info['agenda']:
                missing_items.append("the meeting agenda/purpose")

            # Join the missing items with proper grammar
            if len(missing_items) > 1:
                missing_items[-1] = "and " + missing_items[-1]
            missing_info_text = ", ".join(missing_items) if len(missing_items) > 2 else " ".join(missing_items)

            return f"""Dear {sender_name},

Thank you for your meeting request. To help me properly schedule our meeting, could you please specify {missing_info_text}?

Best regards,
Ivaylo's AI Assistant"""

        # If we have all required information, check availability
        if not self.check_availability(proposed_date, proposed_time):
            return f"""Dear {sender_name},

Thank you for your meeting request. I will review your proposed meeting time ({proposed_date} at {proposed_time}) and get back to you within 24 hours.

Best regards,
Ivaylo's AI Assistant"""

        # Extract location and agenda for confirmation
        location_match = None
        for pattern in location_patterns:
            match = re.search(pattern, email_content, re.IGNORECASE)
            if match:
                location_match = match.group(1).strip()
                break

        agenda_match = None
        for pattern in agenda_patterns:
            match = re.search(pattern, email_content, re.IGNORECASE)
            if match:
                agenda_match = match.group(1).strip()
                break

        return f"""Dear {sender_name},

Thank you for your meeting request. I am pleased to confirm our meeting on {proposed_date} at {proposed_time} at {location_match} to discuss {agenda_match}.

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
        try:
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

            if not subject or subject.strip() == "":
                subject = "Meeting Request"

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

                # Clean up files after successful processing
                cleanup_success = self.cleanup_files()
                if not cleanup_success:
                    print("Warning: Files cleanup failed after sending email")

                return True
            return False

        except Exception as e:
            print(f"Error processing meeting request: {e}")
            return False


def main():
    """Main function to process meeting requests with enhanced error handling"""
    agent = EmailAgent()
    success_count = 0
    error_count = 0

    try:
        # Process meetings from meeting_mails.json
        with open('meeting_mails.json', 'r') as f:
            meeting_data = json.load(f)

        total_meetings = len(meeting_data.get("meetings", []))

        for meeting in meeting_data.get("meetings", []):
            try:
                result = agent.process_meeting_request(
                    email_id=f"{meeting['date']}_{meeting['time']}_{meeting['sender']['email']}",
                    email_content=f"Meeting request for {meeting['topic']} at {meeting['location']}",
                    sender_info=meeting['sender'],
                    subject=meeting['topic'],
                    proposed_date=meeting['date'],
                    proposed_time=meeting['time']
                )

                if result:
                    success_count += 1
                else:
                    error_count += 1

            except Exception as e:
                print(f"Error processing individual meeting: {e}")
                error_count += 1

        # Print processing summary
        print(f"\nProcessing Summary:")
        print(f"Total meetings: {total_meetings}")
        print(f"Successfully processed: {success_count}")
        print(f"Failed to process: {error_count}")

    except Exception as e:
        print(f"Critical error during meeting processing: {e}")

    # Final cleanup attempt if any emails were processed successfully
    if success_count > 0:
        agent.cleanup_files()


if __name__ == "__main__":
    main()