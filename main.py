import asyncio
import json
import logging
from datetime import datetime
from typing import Optional

from gmail import main as gmail_fetch
from mail_sorter import MeetingSorter
from email_writer import EmailAgent
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/main.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def log_execution(message: str):
    """Log execution with timestamp"""
    timestamp = datetime.now().isoformat()
    logger.info(f"[{timestamp}] {message}")


async def process_new_emails() -> bool:
    """Process new emails with enhanced error handling and logging"""
    log_execution("Starting email processing cycle")

    try:
        # Step 1: Fetch new emails from Gmail
        log_execution("Fetching emails from Gmail...")
        gmail_fetch()

        # Step 2: Sort and extract meeting requests
        log_execution("Sorting meeting requests...")
        sorter = MeetingSorter()
        sort_result = await sorter.process_emails("emails.txt")
        log_execution(f"Sort result: {sort_result}")

        # Step 3: Process and respond to meeting requests
        log_execution("Processing meeting requests...")
        agent = EmailAgent()

        try:
            with open('data/cache/meeting_mails.json', 'r') as f:
                meeting_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"Error reading meeting data: {str(e)}")
            return False

        # Track processing results
        processed_count = 0
        success_count = 0

        for meeting in meeting_data.get("meetings", []):
            processed_count += 1
            email_id = f"{meeting['date']}_{meeting['time']}_{meeting['sender']['email']}"

            if not agent.has_responded(email_id):
                log_execution(f"Processing new meeting request: {email_id}")

                success = await agent.process_meeting_request(
                    email_id=email_id,
                    email_content=f"Meeting request for {meeting.get('topic', 'Discussion')} at {meeting.get('location', 'TBD')}",
                    sender_info=meeting['sender'],
                    subject=meeting.get('topic', 'Meeting Request'),
                    proposed_date=meeting['date'],
                    proposed_time=meeting['time']
                )

                if success:
                    success_count += 1
                    log_execution(f"Successfully responded to meeting request: {email_id}")
                else:
                    logger.error(f"Failed to respond to meeting request: {email_id}")
            else:
                log_execution(f"Skipping already processed meeting request: {email_id}")

        # Log processing summary
        log_execution(f"Email processing cycle completed. "
                      f"Processed: {processed_count}, "
                      f"Successful: {success_count}, "
                      f"Failed: {processed_count - success_count}")

        return True

    except Exception as e:
        logger.error(f"Error during email processing: {str(e)}", exc_info=True)
        return False


if __name__ == "__main__":
    load_dotenv(override=True)

    log_execution("Starting one-time email processing...")
    asyncio.run(process_new_emails())
    log_execution("Processing complete")