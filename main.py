from gmail import main as gmail_fetch
from mail_sorter import MeetingSorter
from email_writer import EmailAgent
import json
from datetime import datetime

def log_execution(message):
    timestamp = datetime.now().isoformat()
    print(f"[{timestamp}] {message}")

def process_new_emails():
    log_execution("Starting email processing cycle")
    
    try:
        # Step 1: Fetch new emails from Gmail
        log_execution("Fetching emails from Gmail...")
        gmail_fetch()
        
        # Step 2: Sort and extract meeting requests
        log_execution("Sorting meeting requests...")
        sorter = MeetingSorter()
        sort_result = sorter.process_emails("emails.txt")
        log_execution(f"Sort result: {sort_result}")
        
        # Step 3: Process and respond to meeting requests
        log_execution("Processing meeting requests...")
        agent = EmailAgent()
        
        # Read the latest meeting requests
        with open('meeting_mails.json', 'r') as f:
            meeting_data = json.load(f)
        
        # Process each meeting request
        for meeting in meeting_data["meetings"]:
            email_id = f"{meeting['date']}_{meeting['time']}_{meeting['sender']['email']}"
            
            # Check if we've already responded to this meeting request
            if not agent.has_responded(email_id):
                log_execution(f"Processing new meeting request: {email_id}")
                
                success = agent.process_meeting_request(
                    email_id=email_id,
                    email_content=f"Meeting request for {meeting['topic']} at {meeting['location']}",
                    sender_info=meeting['sender'],
                    subject=meeting['topic'],
                    proposed_date=meeting['date'],
                    proposed_time=meeting['time']
                )
                
                if success:
                    log_execution(f"Successfully responded to meeting request: {email_id}")
                else:
                    log_execution(f"Failed to respond to meeting request: {email_id}")
            else:
                log_execution(f"Skipping already processed meeting request: {email_id}")
                
        log_execution("Email processing cycle completed")
        return True
        
    except Exception as e:
        log_execution(f"Error during email processing: {str(e)}")
        return False

if __name__ == "__main__":
    log_execution("Starting one-time email processing...")
    process_new_emails()
    log_execution("Processing complete")
