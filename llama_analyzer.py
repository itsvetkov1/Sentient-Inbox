import logging
from typing import Dict, Tuple
from email_classifier import EmailTopic
from groq_integration.client_wrapper import EnhancedGroqClient
from config.analyzer_config import ANALYZER_CONFIG

logger = logging.getLogger(__name__)

class LlamaAnalyzer:
    def __init__(self):
        self.client = EnhancedGroqClient()
        self.model_config = ANALYZER_CONFIG["default_analyzer"]["model"]

    async def analyze_email(self, message_id: str, subject: str, content: str, sender: str, email_type: EmailTopic) -> Tuple[str, Dict]:
        """
        Analyze email content using the llama-3.3-70b-versatile model.

        Args:
            message_id: Unique email identifier
            subject: Email subject line
            content: Email body content
            sender: Email sender address
            email_type: Type of email (e.g., meeting, general)

        Returns:
            Tuple of (recommendation, analysis_metadata)
        """
        try:
            prompt = self._construct_prompt(subject, content, sender, email_type)
            messages = [{"role": "user", "content": prompt}]
            response = await self.client.process_with_retry(
                messages=messages,
                model=self.model_config["name"],
                temperature=self.model_config["temperature"],
                max_completion_tokens=self.model_config["max_tokens"]
            )

            analysis = self._parse_response(response.choices[0].message.content)
            recommendation = self._determine_recommendation(analysis)

            logger.info(f"LlamaAnalyzer completed analysis for {message_id}")
            return recommendation, analysis
        except Exception as e:
            logger.error(f"Error in LlamaAnalyzer for email {message_id}: {e}")
            return "needs_review", {}

    def _construct_prompt(self, subject: str, content: str, sender: str, email_type: EmailTopic) -> str:
        """
        Construct the prompt for the llama-3.3-70b-versatile model.
        """
        return f"""
        Analyze the following email:

        Subject: {subject}
        From: {sender}
        Type: {email_type.value}

        Content:
        {content}

        Provide a detailed analysis including:
        1. Key points of the email
        2. Sentiment analysis
        3. Urgency level
        4. Any action items or requests
        5. Relevance to the recipient's role or organization

        Format your response as a JSON object with these keys.
        """

    def _parse_response(self, response: str) -> Dict:
        """
        Parse the model's response into a structured format.
        """
        # Implement parsing logic here
        # This is a placeholder and should be replaced with actual parsing code
        return {
            "key_points": [],
            "sentiment": "",
            "urgency": "",
            "action_items": [],
            "relevance": ""
        }

    def _determine_recommendation(self, analysis: Dict) -> str:
        """
        Determine the recommendation based on the analysis.
        """
        # Implement recommendation logic here
        # This is a placeholder and should be replaced with actual recommendation logic
        return "needs_review"
