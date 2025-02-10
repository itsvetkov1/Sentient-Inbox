import os
from openai import OpenAI
import json
from dotenv import load_dotenv
from datetime import datetime, timedelta
import email.utils

load_dotenv(override=True)


class MeetingSorter:
    def __init__(self):
        self.client = OpenAI()
        self.json_file = "meeting_mails.json"

    def parse_email_content(self, raw_content: str) -> dict:
        """Parse the raw email content into structured format."""
        email_data = {"headers": {}, "body": ""}

        # Skip the "Number of starred emails:" line
        content_lines = raw_content.split('\n')[2:]

        # Parse headers
        current_section = "headers"
        for line in content_lines:
            if line.startswith('Body:'):
                current_section = "body"
                continue
            elif line.strip() == '' or line.startswith('----'):
                continue

            if current_section == "headers":
                if ': ' in line:
                    key, value = line.split(': ', 1)
                    email_data["headers"][key] = value
            else:
                email_data["body"] += line + "\n"

        return email_data

    def extract_meeting_details(self, emails_content: str) -> str:
        """Extract meeting information from email content."""
        # Parse the email first
        email_data = self.parse_email_content(emails_content)

        # Extract sender name and email from the From header
        from_header = email_data['headers'].get('From', '')
        sender_name = from_header.split(' <')[0] if ' <' in from_header else from_header
        sender_email = from_header.split('<')[-1].rstrip('>') if '<' in from_header else from_header

        # Format the email data for the AI to process
        formatted_content = f"""
From: {from_header}
Subject: {email_data['headers'].get('Subject', '')}
Date: {email_data['headers'].get('Date', '')}
Content: {email_data['body']}
"""

        system_prompt = """You are an email analyzer focused on identifying meeting requests.
        When analyzing emails, look for:
        1. Explicit meeting requests
        2. Date and time mentions (including relative terms like 'tomorrow', 'next week')
        3. Meeting topics or purposes
        4. Location information if provided

        Return a JSON response in this exact format:
        {
            "found_meetings": boolean,
            "meetings": [
                {
                    "date": "YYYY-MM-DD",
                    "time": "HH:MM",
                    "topic": "string",
                    "sender_name": "string",
                    "sender_email": "string",
                    "location": "string or null"
                }
            ]
        }

        For relative dates like 'tomorrow', calculate the actual date based on the email's sent date.
        If no specific time is mentioned, do not make assumptions - mark the meeting as not found.
        """

        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": formatted_content}
                ],
                temperature=0.1
            )

            content = response.choices[0].message.content.strip()
            print(f"OpenAI Response: {content}")  # Debug logging

            try:
                # Validate JSON response
                parsed_json = json.loads(content)
                # If we have meetings, process relative dates
                if parsed_json.get("found_meetings", False):
                    email_date = email.utils.parsedate_to_datetime(email_data['headers'].get('Date', ''))
                    for meeting in parsed_json["meetings"]:
                        if meeting.get("date") == "tomorrow":
                            next_day = email_date + timedelta(days=1)
                            meeting["date"] = next_day.strftime("%Y-%m-%d")
                return json.dumps(parsed_json)
            except json.JSONDecodeError:
                print("Failed to parse JSON response")  # Debug logging
                return json.dumps({"found_meetings": False, "meetings": []})

        except Exception as e:
            print(f"Error during OpenAI API call: {str(e)}")
            raise

    def process_emails(self, email_file_path: str) -> str:
        """Process emails from a file and extract meeting information.

        This is the main entry point used by the main.py script.
        """
        try:
            # Read the email file
            with open(email_file_path, 'r', encoding='utf-8') as file:
                emails_content = file.read()

            # Extract meeting details
            json_response = self.extract_meeting_details(emails_content)

            # Save to JSON file for persistence
            self.save_to_json(json_response)

            # Format results for display
            return self.format_results(json_response)

        except UnicodeDecodeError:
            # Try alternative encoding if UTF-8 fails
            try:
                with open(email_file_path, 'r', encoding='latin-1') as file:
                    emails_content = file.read()

                json_response = self.extract_meeting_details(emails_content)
                self.save_to_json(json_response)
                return self.format_results(json_response)

            except Exception as e:
                return f"Error processing emails with alternative encoding: {str(e)}"
        except FileNotFoundError:
            return "Error: Email file not found."
        except Exception as e:
            return f"Error processing emails: {str(e)}"

    def format_results(self, json_response: str) -> str:
        """Format the JSON response into a readable string."""
        try:
            data = json.loads(json_response)
        except json.JSONDecodeError:
            return "Error: Could not parse meeting data"

        if not data.get("found_meetings", False):
            return "No meeting emails found."

        output = "Meeting-related emails found:\n\n"
        for meeting in data.get("meetings", []):
            output += f"Date: {meeting.get('date', 'Not specified')}\n"
            output += f"Time: {meeting.get('time', 'Not specified')}\n"
            output += f"Topic: {meeting.get('topic', 'Not specified')}\n"
            output += f"From: {meeting.get('sender_name', 'Unknown')} <{meeting.get('sender_email', 'unknown')}>\n"
            if meeting.get('location'):
                output += f"Location: {meeting['location']}\n"
            output += "-" * 50 + "\n"

        return output

    def save_to_json(self, json_response: str) -> None:
        """Save the extracted meeting information to a JSON file."""
        try:
            data = json.loads(json_response)
        except json.JSONDecodeError:
            print("Error: Invalid JSON response")
            return

        current_time = datetime.now().isoformat()

        try:
            with open(self.json_file, 'r') as f:
                stored_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            stored_data = {
                "last_updated": current_time,
                "meetings": []
            }

        # Add new meetings only if they don't exist
        if data.get("found_meetings", False):
            for new_meeting in data.get("meetings", []):
                if not any(
                        existing_meeting.get("date") == new_meeting.get("date") and
                        existing_meeting.get("time") == new_meeting.get("time") and
                        existing_meeting.get("topic", "").lower() == new_meeting.get("topic", "").lower() and
                        existing_meeting.get("sender", {}).get("email") == new_meeting.get("sender_email")
                        for existing_meeting in stored_data.get("meetings", [])
                ):
                    stored_data["meetings"].append({
                        "date": new_meeting.get("date"),
                        "time": new_meeting.get("time"),
                        "topic": new_meeting.get("topic"),
                        "sender": {
                            "name": new_meeting.get("sender_name"),
                            "email": new_meeting.get("sender_email")
                        },
                        "location": new_meeting.get("location"),
                        "added_on": current_time
                    })

        stored_data["last_updated"] = current_time

        # Write back to file with pretty printing
        with open(self.json_file, 'w') as f:
            json.dump(stored_data, f, indent=2, sort_keys=True, ensure_ascii=False)