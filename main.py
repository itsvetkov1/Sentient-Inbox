import asyncio
import logging
import sys
from datetime import datetime
from pathlib import Path

# Add src directory to Python path
sys.path.append(str(Path(__file__).parent / "src"))

from integrations.gmail.client import GmailClient
from email_processing.processor import EmailProcessor
from email_processing.classification.classifier import EmailTopic
from email_processing.handlers.writer import EmailAgent
from email_processing.analyzers.llama import LlamaAnalyzer
from email_processing.analyzers.deepseek import DeepseekAnalyzer
from storage.secure import SecureStorage
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
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
    logger.debug(f"[{timestamp}] {message}")

# Load environment variables
load_dotenv(override=True)

async def process_email_batch(batch_size: int = 100) -> bool:
    log_execution(f"Starting email processing cycle for batch of {batch_size} emails")

    try:
        gmail_client = GmailClient()
        meeting_agent = EmailAgent()
        llama_analyzer = LlamaAnalyzer()
        deepseek_analyzer = DeepseekAnalyzer()
        secure_storage = SecureStorage()
        processor = EmailProcessor(
            gmail_client=gmail_client,
            llama_analyzer=llama_analyzer,
            deepseek_analyzer=deepseek_analyzer
        )        
        processor.register_agent(EmailTopic.MEETING, meeting_agent)
        
        log_execution("Processing email batch...")
        processed_count, error_count, errors = await processor.process_email_batch(batch_size)
        
        log_execution(f"Email processing cycle completed. "
                     f"Processed: {processed_count}, "
                     f"Errors: {error_count}")
        
        logger.info(f"\nProcessed {processed_count} emails")
        logger.info(f"Encountered {error_count} errors")
        logger.info("Check the log file for detailed model responses and processing information.")
        
        if errors:
            logger.warning("Errors encountered during processing:")
            for error in errors:
                logger.warning(f"- {error}")

        return error_count == 0

    except Exception as e:
        logger.error(f"Error during email processing: {str(e)}", exc_info=True)
        return False

async def main():
    retry_delay = 3  # seconds
    max_retries = 1  # single retry attempt

    for attempt in range(max_retries + 1):
        if attempt > 0:
            logger.info(f"Retry attempt {attempt} after {retry_delay} seconds delay")
            await asyncio.sleep(retry_delay)

        success = await process_email_batch()
        if success:
            break
    
    if not success:
        logger.error("Email processing failed after all retry attempts")

    # Perform maintenance tasks
    await perform_maintenance()

async def perform_maintenance():
    """Perform maintenance tasks such as cleanup and key rotation"""
    try:
        secure_storage = SecureStorage()
        key_rotated = await secure_storage.rotate_key()
        records_cleaned = await secure_storage._cleanup_old_records()
        logger.info(f"Maintenance tasks completed. Key rotated: {key_rotated}, Records cleaned: {records_cleaned}")
    except Exception as e:
        logger.error(f"Error during maintenance tasks: {str(e)}", exc_info=True)

if __name__ == "__main__":
    log_execution("Starting email processing...")
    asyncio.run(main())
    log_execution("Processing complete")
