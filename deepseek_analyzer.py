import logging
from typing import Dict, Tuple
from groq_integration.client_wrapper import EnhancedGroqClient
from email_analyzers_base import BaseEmailAnalyzer
from config.analyzer_config import ANALYZER_CONFIG

logger = logging.getLogger(__name__)

class DeepseekAnalyzer(BaseEmailAnalyzer):
    """
    Analyzer class for deep analysis of meeting emails using Groq's deepseek r1 model.
    """

    def __init__(self, groq_client: EnhancedGroqClient):
        """
        Initialize the DeepseekAnalyzer with an EnhancedGroqClient instance and configuration.

        Args:
            groq_client: An instance of EnhancedGroqClient for making API calls to Groq.
        """
        super().__init__()
        self.groq_client = groq_client
        self.config = ANALYZER_CONFIG["deepseek_analyzer"]
        self.setup_logging()

    def setup_logging(self):
        """Set up logging based on the configuration."""
        log_config = self.config["logging"]
        logging.basicConfig(
            filename=f"{log_config['base_dir']}/deepseek_analyzer.log",
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

    async def analyze_email(self, email_content: str) -> Tuple[str, Dict]:
        """
        Perform deep analysis on the email content using Groq's deepseek r1 model.

        Args:
            email_content: The full content of the email to be analyzed.

        Returns:
            A tuple containing the decision (str) and additional analysis details (Dict).
        """
        prompt = f"""
        Analyze the following email content deeply and decide on the appropriate action:

        {email_content}

        Based on the content, determine:
        1. Does the sender expect a standardized response?
        2. Should the receiver take another action and flag the email?
        3. Should the email be ignored and left unread?

        Provide your decision as one of the following:
        - "standard_response": If a standardized response is expected
        - "flag_for_action": If the receiver should take action and the email should be flagged
        - "ignore": If the email should be ignored and left unread

        Also, provide a brief explanation for your decision.

        Return your response in the following format:
        Decision: [Your decision]
        Explanation: [Your explanation]
        """

        try:
            response = await self.groq_client.generate_text(
                prompt,
                model=self.config["model"]["name"],
                temperature=self.config["model"]["temperature"],
                max_tokens=self.config["model"]["max_tokens"]
            )
            
            # Parse the response
            lines = response.strip().split('\n')
            decision = lines[0].split(': ')[1].strip().lower()
            explanation = ' '.join(lines[1:]).replace('Explanation: ', '').strip()

            logger.info(f"DeepseekAnalyzer decision: {decision}")
            return decision, {"explanation": explanation}
        except Exception as e:
            logger.error(f"Error in DeepseekAnalyzer: {e}")
            return "flag_for_action", {"explanation": "Error occurred during analysis, flagging for manual review."}
