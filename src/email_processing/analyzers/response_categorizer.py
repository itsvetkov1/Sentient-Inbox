# """
# ResponseCategorizer: Final Email Categorization Service

# Implements the final stage of the email analysis pipeline, determining
# appropriate handling categories based on Deepseek's detailed analysis
# and generating appropriate response templates.

# Design Considerations:
# - Comprehensive parameter detection from natural language analysis
# - Prioritization of standard responses for missing parameters
# - Clear communication templates for parameter requests
# - Robust error handling with fallback mechanisms
# - Integration with response management specifications
# """

import logging
import re
from typing import Dict, Tuple, List, Optional
from datetime import datetime
import json

from integrations.groq import EnhancedGroqClient
from config.analyzer_config import ANALYZER_CONFIG

logger = logging.getLogger(__name__)

class ResponseCategorizer:
    # """
    # Final stage analyzer for determining email handling categories and responses.
    
    # Uses Deepseek's analysis to make final categorization decisions and
    # generate appropriate response templates based on missing information
    # or required confirmations.
    
    # Implements the third stage of the three-stage email analysis pipeline,
    # making final determinations about email handling and response generation
    # based on the detailed analysis provided by the Deepseek model.
    # """
    
    def __init__(self):
        """Initialize categorizer with required components."""
        self.client = EnhancedGroqClient()
        self.model_config = ANALYZER_CONFIG["default_analyzer"]["model"]
        logger.debug(f"ResponseCategorizer initialized with model configuration: {self.model_config['name']}")
        
    async def categorize_email(
        self,
        deepseek_summary: str,
        deepseek_recommendation: str
    ) -> Tuple[str, Optional[str]]:
        """
        Determine final handling category and generate response if needed.
        
        Implements intelligent categorization based on Deepseek analysis:
        - For emails with missing date/time/location, generates parameter request
        - For complex emails, categorizes for manual review
        - For irrelevant emails, categorizes for ignoring
        
        Args:
            deepseek_summary: Detailed analysis from Deepseek
            deepseek_recommendation: Recommended handling category
            
        Returns:
            Tuple of (category: str, response_template: Optional[str])
        """
        try:
            logger.info(f"Processing categorization with recommendation: {deepseek_recommendation}")
            
            # Check if missing parameters are mentioned in the summary
            missing_params = self._extract_missing_parameters(deepseek_summary)
            logger.debug(f"Extracted missing parameters: {missing_params}")
            
            # If there are missing parameters but they're requestable, prioritize standard_response
            if missing_params and deepseek_recommendation != "ignore":
                logger.info(f"Found missing parameters: {missing_params}, generating parameter request template")
                response_template = await self._generate_parameter_request(deepseek_summary, missing_params)
                return "standard_response", response_template
                
            if deepseek_recommendation == "standard_response":
                # Extract missing information or generate confirmation
                logger.info("Generating standard response template based on Deepseek recommendation")
                response_template = await self._generate_response_template(deepseek_summary)
                return "standard_response", response_template
                
            elif deepseek_recommendation == "needs_review":
                logger.info("Categorizing email for manual review based on Deepseek recommendation")
                return "needs_review", None
                
            else:  # ignore
                logger.info("Categorizing email for ignoring based on Deepseek recommendation")
                return "ignore", None
                
        except Exception as e:
            logger.error(f"Categorization failed: {str(e)}")
            return "needs_review", None
        
            
    def _extract_missing_parameters(self, summary: str) -> List[str]:
        """
        Extract missing parameters from Deepseek summary.
        
        Analyzes the summary to identify parameters that can be requested
        from the sender, such as date, time, location, or agenda.
        
        Args:
            summary: Detailed summary from Deepseek analysis
            
        Returns:
            List of missing parameter names
        """
        missing_params = []
        
        # Common patterns for missing parameter detection
        missing_patterns = {
            "date": ["missing date", "date is missing", "no date", "without date", "date absent", "date: absent"],
            "time": ["missing time", "time is missing", "am/pm unclear", "am/pm unspecified", "unclear time", "time: absent"],
            "location": ["missing location", "location is missing", "vague location", "unclear location", "location: absent"],
            "agenda": ["missing agenda", "purpose unclear", "no purpose", "unclear purpose", "agenda: absent"]
        }
        
        summary_lower = summary.lower()
        
        for param, patterns in missing_patterns.items():
            if any(pattern in summary_lower for pattern in patterns):
                missing_params.append(param)
                
        return missing_params

    async def _generate_response_template(self, summary: str) -> str:
        """
        Generate appropriate response template based on Deepseek's analysis.
        
        Creates either an information request for missing details or a
        meeting confirmation template based on the analysis content.
        
        Args:
            summary: Detailed analysis from Deepseek
            
        Returns:
            Formatted response template
        """
        try:
            # Analyze summary for missing information
            prompt = self._construct_response_prompt(summary)
            
            logger.debug(f"Sending response generation prompt to model: {len(prompt)} characters")
            response = await self.client.process_with_retry(
                messages=[
                    {"role": "system", "content": "You are an email response generator. Create appropriate meeting-related responses."},
                    {"role": "user", "content": prompt}
                ],
                model=self.model_config["name"],
                temperature=0.7
            )
            
            response_content = response.choices[0].message.content.strip()
            logger.debug(f"Generated response template of length: {len(response_content)}")
            return response_content
            
        except Exception as e:
            logger.error(f"Response template generation failed: {e}")
            return self._get_default_response_template()
        

    async def _generate_parameter_request(self, summary: str, missing_params: List[str]) -> str:
        """
        Generate a response requesting missing parameters.
        
        Creates a polite, structured response requesting specific
        missing information needed to process the meeting.
        
        Args:
            summary: Detailed summary from Deepseek
            missing_params: List of parameters to request
            
        Returns:
            Formatted response template requesting information
        """
        param_descriptions = {
            "date": "the meeting date",
            "time": "the specific time (including AM/PM)",
            "location": "the exact meeting location",
            "agenda": "the meeting purpose or agenda"
        }
        
        formatted_params = [param_descriptions[param] for param in missing_params if param in param_descriptions]
        
        if len(formatted_params) == 1:
            param_text = formatted_params[0]
        elif len(formatted_params) == 2:
            param_text = f"{formatted_params[0]} and {formatted_params[1]}"
        else:
            param_text = ", ".join(formatted_params[:-1]) + f", and {formatted_params[-1]}"
        
        # Extract sender name using regex
        sender_match = re.search(r"sender: ([^,\n]+)", summary)
        sender_name = sender_match.group(1) if sender_match else "[Sender]"
        
        response_template = f"""Dear {sender_name},

Thank you for your meeting request. To help me properly schedule our meeting, could you please provide {param_text}?

Best regards,
Ivaylo's AI Assistant"""

        logger.debug(f"Generated parameter request for: {missing_params}")
        return response_template

    def _construct_response_prompt(self, summary: str) -> str:
        """
        Construct prompt for response template generation.
        
        Creates a focused prompt that emphasizes identifying missing
        information or generating appropriate confirmation messages.
        
        Args:
            summary: Detailed analysis from Deepseek
            
        Returns:
            Structured prompt for response generation
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
        """
        Provide a safe default response template for error cases.
        
        Returns a generalized response that can safely be used when
        specific template generation fails.
        
        Returns:
            Default response template
        """
        return """Dear [Sender],

Thank you for your meeting request. To help me properly schedule our meeting, could you please provide additional details about the proposed meeting?

Best regards,
Ivaylo's AI Assistant"""