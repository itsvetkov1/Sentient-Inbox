import asyncio
import json
import logging
from datetime import datetime
from typing import Optional
from pathlib import Path

from gmail import GmailClient
from email_processor import EmailProcessor
from email_classifier import EmailTopic
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

# Ensure logs directory exists
Path('logs').mkdir(exist_ok=True)

def log_execution(message: str):
    """Log execution with timestamp"""
    timestamp = datetime.now().isoformat()
    logger.info(f"[{timestamp}] {message}")

async def process_new_emails() -> bool:
    """Process new emails with enhanced error handling and logging"""
    log_execution("Starting email processing cycle")

    try:
        # Initialize components
        gmail_client = GmailClient()
        meeting_agent = EmailAgent()
        email_processor = EmailProcessor(gmail_client)
        
        # Register the meeting agent
        email_processor.register_agent(EmailTopic.MEETING, meeting_agent)
        
        # Process unread emails
        log_execution("Processing unread emails...")
        processed_count, error_count, errors = await email_processor.process_unread_emails()
        
        # Log processing summary
        log_execution(f"Email processing cycle completed. "
                     f"Processed: {processed_count}, "
                     f"Errors: {error_count}")
        
        # Log any errors
        if errors:
            logger.warning("Errors encountered during processing:")
            for error in errors:
                logger.warning(f"- {error}")

        return error_count == 0

    except Exception as e:
        logger.error(f"Error during email processing: {str(e)}", exc_info=True)
        return False

if __name__ == "__main__":
    load_dotenv(override=True)

    log_execution("Starting one-time email processing...")
    asyncio.run(process_new_emails())
    log_execution("Processing complete")
