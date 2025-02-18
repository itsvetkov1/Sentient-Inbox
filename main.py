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
from llama_analyzer import LlamaAnalyzer
from deepseek_analyzer import DeepseekAnalyzer
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

# Load environment variables
load_dotenv(override=True)

# In main.py
async def process_new_emails() -> bool:
    log_execution("Starting email processing cycle")

    try:
        gmail_client = GmailClient()
        meeting_agent = EmailAgent()
        llama_analyzer = LlamaAnalyzer()
        deepseek_analyzer = DeepseekAnalyzer()
        email_processor = EmailProcessor(gmail_client, llama_analyzer, deepseek_analyzer)
        
        email_processor.register_agent(EmailTopic.MEETING, meeting_agent)
        
        log_execution("Processing unread emails...")
        processed_count, error_count, errors = await email_processor.process_unread_emails()
        
        log_execution(f"Email processing cycle completed. "
                     f"Processed: {processed_count}, "
                     f"Errors: {error_count}")
        
        print(f"\nProcessed {processed_count} emails")
        print(f"Encountered {error_count} errors")
        print("Check the console output above for model responses.")
        
        if errors:
            logger.warning("Errors encountered during processing:")
            for error in errors:
                logger.warning(f"- {error}")

        return error_count == 0

    except Exception as e:
        logger.error(f"Error during email processing: {str(e)}", exc_info=True)
        return False

if __name__ == "__main__":
    log_execution("Starting one-time email processing...")
    asyncio.run(process_new_emails())
    log_execution("Processing complete")
