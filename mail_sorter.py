import os
from openai import OpenAI
from typing import List, Dict, Optional
import json
from dotenv import load_dotenv
from datetime import datetime

load_dotenv(override=True)

class MeetingSorter:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.json_file = "meeting_mails.json"

    def extract_meeting_details(self, emails_content: str) -> str:
        # System prompt to guide the AI in analyzing emails
        system_prompt = """
        Analyze the provided emails and extract meeting-related information. 
        For each meeting-related email, extract:
        - Meeting date and time
        - Meeting topic/purpose
        - Sender's name
        - Sender's email
        - Location (if provided)
        
        Return the results in JSON format like this:
        {
            "found_meetings": true/false,
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
        
        If no meeting-related emails are found, return: {"found_meetings": false, "meetings": []}
        """

        # Make API call to analyze emails
        response = self.client.chat.completions.create(
            model="gpt-4o",  # or another suitable model
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": emails_content}
            ],
            response_format={"type": "json_object"}
        )

        return response.choices[0].message.content

    def format_results(self, json_response: str) -> str:
        data = json.loads(json_response)
        
        if not data["found_meetings"]:
            return "No meeting emails found."
        
        output = "Meeting-related emails found:\n\n"
        for meeting in data["meetings"]:
            output += f"Date: {meeting['date']}\n"
            output += f"Time: {meeting['time']}\n"
            output += f"Topic: {meeting['topic']}\n"
            output += f"From: {meeting['sender_name']} <{meeting['sender_email']}>\n"
            if meeting['location']:
                output += f"Location: {meeting['location']}\n"
            output += "-" * 50 + "\n"
        
        return output

    def save_to_json(self, json_response: str) -> None:
        data = json.loads(json_response)
        
        if not data["found_meetings"]:
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
        for new_meeting in data["meetings"]:
            # Check if meeting already exists
            is_duplicate = False
            for existing_meeting in stored_data["meetings"]:
                if (
                    existing_meeting["date"] == new_meeting["date"] and
                    existing_meeting["time"] == new_meeting["time"] and
                    existing_meeting["topic"].lower() == new_meeting["topic"].lower() and
                    existing_meeting["sender"]["email"] == new_meeting["sender_email"]
                ):
                    is_duplicate = True
                    break
            
            # Only add if it's not a duplicate
            if not is_duplicate:
                stored_data["meetings"].append({
                    "date": new_meeting["date"],
                    "time": new_meeting["time"],
                    "topic": new_meeting["topic"],
                    "sender": {
                        "name": new_meeting["sender_name"],
                        "email": new_meeting["sender_email"]
                    },
                    "location": new_meeting["location"],
                    "added_on": current_time
                })
        
        stored_data["last_updated"] = current_time
        
        # Write back to file with pretty printing
        with open(self.json_file, 'w') as f:
            json.dump(stored_data, f, indent=2, sort_keys=True, ensure_ascii=False)

    def process_emails(self, email_file_path: str) -> str:
        try:
            # Try UTF-8 first
            with open(email_file_path, 'r', encoding='utf-8') as file:
                emails_content = file.read()
            
            json_response = self.extract_meeting_details(emails_content)
            self.save_to_json(json_response)  # Save to JSON file
            return self.format_results(json_response)
            
        except UnicodeDecodeError:
            # If UTF-8 fails, try with latin-1
            try:
                with open(email_file_path, 'r', encoding='latin-1') as file:
                    emails_content = file.read()
                
                json_response = self.extract_meeting_details(emails_content)
                self.save_to_json(json_response)  # Save to JSON file
                return self.format_results(json_response)
                
            except Exception as e:
                return f"Error processing emails with alternative encoding: {str(e)}"
        except FileNotFoundError:
            return "Error: Email file not found."
        except Exception as e:
            return f"Error processing emails: {str(e)}"

def main():
    sorter = MeetingSorter()
    result = sorter.process_emails("emails.txt")
    print(result)

if __name__ == "__main__":
    main()
