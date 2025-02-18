import logging
import aiohttp
import json
import os
from typing import Dict, Tuple
from email_analyzers_base import BaseEmailAnalyzer
from config.analyzer_config import ANALYZER_CONFIG

logger = logging.getLogger(__name__)

class DeepseekAnalyzer(BaseEmailAnalyzer):
    """
    Analyzer class for deep analysis of meeting emails using DeepSeek's reasoner model.
    """

    def __init__(self):
        """Initialize the DeepseekAnalyzer with configuration."""
        super().__init__()
        self.config = ANALYZER_CONFIG["deepseek_analyzer"]
        self.api_key = os.environ.get("DEEPSEEK_API_KEY")
        if not self.api_key:
            raise ValueError("DEEPSEEK_API_KEY environment variable is not set")
        self.api_endpoint = self.config["model"]["api_endpoint"]
        self.setup_logging()

    def setup_logging(self):
        """Set up detailed logging for debugging."""
        log_config = self.config["logging"]
        logging.basicConfig(
            filename=f"{log_config['base_dir']}/deepseek_analyzer.log",
            level=logging.DEBUG,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

    async def analyze_email(self, email_content: str) -> Tuple[str, Dict]:
        """
        Perform deep analysis on the email content using DeepSeek's reasoner model.
        
        Args:
            email_content: The full content of the email to be analyzed.
            
        Returns:
            Tuple[str, Dict]: Decision and analysis details
        """
        # Log the input
        logger.debug(f"Analyzing email content: {email_content[:200]}...")

        prompt = self._construct_prompt(email_content)
        
        try:
            async with aiohttp.ClientSession() as session:
                # Log request payload
                request_payload = {
                    "model": self.config["model"]["name"],
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": self.config["model"]["temperature"],
                    "max_tokens": self.config["model"]["max_tokens"]
                }
                logger.debug(f"Request payload: {json.dumps(request_payload, indent=2)}")

                async with session.post(
                    f"{self.api_endpoint}/chat/completions",
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {self.api_key}"
                    },
                    json=request_payload
                ) as response:
                    # Log raw response
                    response_text = await response.text()
                    logger.debug(f"Raw API response: {response_text}")
                    
                    if response.status != 200:
                        raise Exception(f"API request failed with status {response.status}: {response_text}")
                    
                    result = json.loads(response_text)
                    
                    # Log parsed response structure
                    logger.debug(f"Parsed API response structure: {json.dumps(result, indent=2)}")
                    
                    if "choices" not in result or not result["choices"]:
                        logger.error("No choices in API response")
                        raise ValueError("No choices in API response")
                        
                    choice = result["choices"][0]
                    if "message" not in choice:
                        logger.error(f"No message in choice: {json.dumps(choice, indent=2)}")
                        raise ValueError("No message in choice")
                        
                    content = choice["message"].get("content")
                    if not content:
                        logger.error("Empty or missing content in message")
                        raise ValueError("Empty or missing content")

                    # Log the content for analysis
                    logger.debug(f"Extracted content: {content}")
                    
                    # Parse the response
                    decision, explanation = self._parse_response(content)
                    
                    logger.info(f"Analysis complete - Decision: {decision}")
                    logger.info(f"Full explanation: {explanation}")
                    return decision, {"explanation": explanation}

        except Exception as e:
            logger.error(f"Error in DeepseekAnalyizer: {str(e)}", exc_info=True)
            return "flag_for_action", {
                "explanation": f"Error occurred during analysis, flagging for manual review. Error: {str(e)}"
            }

    def _construct_prompt(self, email_content: str) -> str:
        """Construct the analysis prompt."""
        return f"""
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
        Decision: [standard_response/flag_for_action/ignore]
        Explanation: [Provide your complete explanation here, including all relevant details and reasoning]
        """

    def _parse_response(self, content: str) -> Tuple[str, str]:
        """Parse the model's response into decision and explanation."""
        lines = content.strip().split('\n')
        if len(lines) < 2:
            raise ValueError(f"Insufficient content in response: {content}")
            
        decision_line = lines[0].split(':', 1)
        if len(decision_line) < 2:
            raise ValueError(f"Invalid decision format: {lines[0]}")
            
        decision = decision_line[1].strip().lower()
        # Collect all lines after "Decision:" for the explanation
        explanation_lines = []
        in_explanation = False
        for line in lines:
            if line.strip().startswith('Explanation:'):
                in_explanation = True
                # Remove the "Explanation:" prefix from this line
                current_line = line.replace('Explanation:', '', 1).strip()
                if current_line:  # Only add if there's content after "Explanation:"
                    explanation_lines.append(current_line)
            elif in_explanation:
                explanation_lines.append(line.strip())
        
        explanation = ' '.join(explanation_lines).strip()
        
        if not decision or not explanation:
            raise ValueError("Missing decision or explanation")
            
        # Log parsed components
        logger.debug(f"Parsed decision: {decision}")
        logger.debug(f"Parsed explanation: {explanation}")
        
        return decision, explanation