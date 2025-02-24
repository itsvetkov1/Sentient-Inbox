"""
ResponseCategorizer: Final Email Categorization Service

Implements the final stage of the email analysis pipeline, determining
appropriate handling categories based on Deepseek's detailed analysis
and generating appropriate response templates.
"""

import logging
import re
from typing import Dict, Tuple, List, Optional
from datetime import datetime
import json

from integrations.groq import EnhancedGroqClient
from config.analyzer_config import ANALYZER_CONFIG

logger = logging.getLogger(__name__)

class ResponseCategorizer:
    """
    Final stage analyzer for determining email handling categories and responses.
    
    Uses Deepseek's analysis to make final categorization decisions and
    generate appropriate response templates based on missing information
    or required confirmations.
    """
    
    def __init__(self):
        """Initialize categorizer with required components."""
        self.client = EnhancedGroqClient()
        self.model_config = ANALYZER_CONFIG["default_analyzer"]["model"]
        
    async def categorize_email(
        self,
        deepseek_summary: str,
        deepseek_recommendation: str
    ) -> Tuple[str, Optional[str]]:
        """
        Determine final handling category and generate response if needed.
        
        Args:
            deepseek_summary: Detailed analysis from Deepseek
            deepseek_recommendation: Recommended handling category
            
        Returns:
            Tuple of (category: str, response_template: Optional[str])
        """
        try:
            logger.info(f"Processing categorization with recommendation: {deepseek_recommendation}")
            
            if deepseek_recommendation == "standard_response":
                # Extract missing information or generate confirmation
                response_template = await self._generate_response_template(deepseek_summary)
                return "standard_response", response_template
                
            elif deepseek_recommendation == "needs_review":
                return "needs_review", None
                
            else:  # ignore
                return "ignore", None
                
        except Exception as e:
            logger.error(f"Categorization failed: {str(e)}")
            return "needs_review", None

    async def _generate_response_template(self, summary: str) -> str:
        """
        Generate appropriate response template based on Deepseek's analysis.
        
        Creates either an information request for missing details or a
        meeting confirmation template based on the analysis content.
        """
        try:
            # Analyze summary for missing information
            prompt = self._construct_response_prompt(summary)
            
            response = await self.client.process_with_retry(
                messages=[
                    {"role": "system", "content": "You are an email response generator. Create appropriate meeting-related responses."},
                    {"role": "user", "content": prompt}
                ],
                model=self.model_config["name"],
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Response template generation failed: {e}")
            return self._get_default_response_template()

    def _construct_response_prompt(self, summary: str) -> str:
        """
        Construct prompt for response template generation.
        
        Creates a focused prompt that emphasizes identifying missing
        information or generating appropriate confirmation messages.
        """
        return f"""
        Based on this meeting email analysis, generate an appropriate response:

        {summary}

        If date, time, or location is missing:
        - Create a polite request for the specific missing information
        
        If all meeting details are present:
        - Create a confirmation message for meeting attendance
        
        Requirements:
        - Keep the response professional but friendly
        - Be specific about what information is missing
        - For confirmations, reflect key meeting details
        - Start with "Dear [Sender]" and end with "Best regards"
        """

    def _get_default_response_template(self) -> str:
        """Provide a safe default response template for error cases."""
        return """Dear [Sender],

Thank you for your meeting request. To help me properly schedule our meeting, could you please provide additional details about the proposed meeting?

Best regards,
[Assistant]"""