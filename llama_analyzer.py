import logging
from typing import Dict, Tuple, Any
import json  # Import the json module
from email_classifier import EmailTopic
from groq_integration.client_wrapper import EnhancedGroqClient  # Corrected import
from config.analyzer_config import ANALYZER_CONFIG

logger = logging.getLogger(__name__)


class LlamaAnalyzer:
    def __init__(self):
        self.client = EnhancedGroqClient()
        self.model_config = ANALYZER_CONFIG["default_analyzer"]["model"]

    async def analyze_email(
        self,
        message_id: str,
        subject: str,
        content: str,
        sender: str,
        email_type: EmailTopic,
    ) -> Tuple[str, Dict]:
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
                max_completion_tokens=self.model_config["max_tokens"],
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

        Format your response as a valid JSON object with these keys:
        {
            "key_points": [],
            "sentiment": "",
            "urgency": "",
            "action_items": [],
            "relevance": ""
        }
        Ensure that your response is a properly formatted JSON object that can be parsed by Python's json.loads() function.
        """

    def _parse_response(self, response: str) -> Dict:
        """
        Parse the model's response into a structured format.
        """
        # Implement parsing logic here
        # This is a placeholder and should be replaced with actual parsing code
        #  Attempt to parse as JSON, and return a default structure on failure.
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            logger.warning("Failed to parse response as JSON. Returning default values.")
            return {
                "key_points": [],
                "sentiment": "",
                "urgency": "",
                "action_items": [],
                "relevance": "",
            }

    def _determine_recommendation(self, analysis: Dict) -> str:
        """
        Determine the recommendation based on the analysis.
        """
        # Implement recommendation logic here
        # This is a placeholder and should be replaced with actual recommendation logic
        return "needs_review"

    async def process_deepseek_analysis(self, deepseek_output: str) -> Tuple[str, Dict[str, Any]]:
        """
        Process DeepSeek's natural language analysis into structured decision format.

        Takes DeepSeek's detailed analysis and converts it into actionable
        decisions with supporting metadata. Implements comprehensive parsing
        and validation of the analysis content.

        Args:
            deepseek_output: Structured analysis from DeepSeek

        Returns:
            Tuple containing decision and supporting analysis
        """
        try:
            prompt = [
                {
                    "role": "system",
                    "content": """You are an expert email analyzer. Based on the provided
                    analysis, determine the appropriate action category and provide
                    structured reasoning. Respond in JSON format with the following structure:
                    {
                        "decision": "standard_response" | "flag_for_action" | "ignore",
                        "confidence": 0.0 to 1.0,
                        "reasoning": "Brief explanation of decision",
                        "urgency": "high" | "medium" | "low",
                        "action_required": true | false
                    }""",
                },
                {
                    "role": "user",
                    "content": f"Analysis to evaluate:\n\n{deepseek_output}",
                },
            ]

            response = await self.client.process_with_retry(
                messages=prompt,
                model=self.model_config["name"],
                temperature=0.3,
                response_format={"type": "json_object"},
            )

            result = json.loads(response.choices[0].message.content)

            return result["decision"], {
                "confidence": result["confidence"],
                "reasoning": result["reasoning"],
                "urgency": result["urgency"],
                "action_required": result["action_required"],
                "source": "llama",
                "deepseek_analysis": deepseek_output,
            }

        except Exception as e:
            logger.error(f"Error processing DeepSeek analysis: {str(e)}", exc_info=True)
            return "needs_review", {
                "error": str(e),
                "deepseek_analysis": deepseek_output,
            }
