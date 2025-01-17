from openai import OpenAI
import json
from gmail import SCOPES, build
from google.oauth2.credentials import Credentials
import base64
from email.mime.text import MIMEText
from dotenv import load_dotenv
import os
from datetime import datetime
load_dotenv(override=True)

class EmailAgent:
    def __init__(self):
        self.client = OpenAI()
        self.load_schedule()
        self.load_response_log()
        self.setup_gmail_service()

    def load_schedule(self):
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
        try:
            with open('email_responses.json', 'r') as f:
                content = f.read().strip()
                if content:  # Check if file has content
                    self.response_log = json.load(f)
                else:
                    self.response_log = {"responses": []}
        except (FileNotFoundError, json.JSONDecodeError):
            self.response_log = {"responses": []}
            # Create the file with default structure
            with open('email_responses.json', 'w') as f:
                json.dump(self.response_log, f, indent=2)

    def save_response_log(self, email_id, response_data):
        self.response_log["responses"].append({
            "email_id": email_id,
            "response_time": datetime.now().isoformat(),
            "response_data": response_data
        })
        with open('email_responses.json', 'w') as f:
            json.dump(self.response_log, f, indent=2)

    def has_responded(self, email_id):
        return any(r["email_id"] == email_id for r in self.response_log["responses"])

    def setup_gmail_service(self):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        self.service = build('gmail', 'v1', credentials=creds)

    def check_availability(self, date, time):
        for meeting in self.schedule['meetings']:
            if meeting['date'] == date and meeting['time'] == time:
                return False
        return True

    def create_response(self, email_content, sender_name, proposed_date, proposed_time):
        # Create system prompt with context
        system_prompt = """you are an email assistant that responds to meeting requests. 
        you always write in lowercase and keep responses very concise and casual. 
        use a friendly tone but get straight to the point."""

        # Combine email context with availability check
        is_available = self.check_availability(proposed_date, proposed_time)
        context = f"""
        original email: {email_content}
        sender: {sender_name}
        proposed date: {proposed_date}
        proposed time: {proposed_time}
        is available: {is_available}
        current schedule: {json.dumps(self.schedule['meetings'], indent=2)}
        """

        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": context}
            ]
        )

        return response.choices[0].message.content

    def send_email(self, to_email, subject, message_text):
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
