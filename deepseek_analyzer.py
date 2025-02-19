import logging
import aiohttp
import os
from typing import Dict, Tuple, Any, Optional
from email_analyzers_base import BaseEmailAnalyzer
from config.analyzer_config import ANALYZER_CONFIG

logger = logging.getLogger(__name__)

class DeepseekAnalyzer(BaseEmailAnalyzer):
    """
    Specialized deep analysis component leveraging DeepSeek's natural language capabilities.
    
    This implementation provides rich, contextual analysis of email content without
    requiring structured JSON output. The analysis is later processed by LlamaAnalyzer
    for final decision-making.
    
    Key Features:
    - Detailed natural language analysis
    - Comprehensive error handling
    - Robust prompt engineering
    - Integration with LlamaAnalyzer workflow
    """

    def __init__(self):
        """
        Initialize analyzer with required configuration and logging infrastructure.
        
        Validates environment settings and establishes logging pathways for
        production monitoring and debugging capabilities.
        """
        super().__init__()
        self.config = ANALYZER_CONFIG["deepseek_analyzer"]
        self.api_key = os.environ.get("DEEPSEEK_API_KEY")
        if not self.api_key:
            raise ValueError("DEEPSEEK_API_KEY environment variable is not set")
        self.api_endpoint = self.config["model"]["api_endpoint"]
        self._setup_logging()

    def _setup_logging(self) -> None:
        """Configure comprehensive logging infrastructure."""
        log_config = self.config["logging"]
        logging.basicConfig(
            filename=f"{log_config['base_dir']}/deepseek_analyzer.log",
            level=logging.DEBUG,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

    def _construct_prompt(self, email_content: str) -> str:
        """
        Construct analysis prompt optimized for natural language response.
        
        Creates a carefully engineered prompt that encourages detailed analysis
        while maintaining consistent response structure for later processing.
        
        Args:
            email_content: Raw email content for analysis
            
        Returns:
            str: Structured prompt for the DeepSeek model
        """
        return f"""
        Analyze this email deeply and provide a comprehensive summary:

        EMAIL CONTENT:
        {email_content}

        Provide your analysis in the following structure:

        MEETING DETAILS:
        - Purpose: [Main purpose of discussed meeting(s)]
        - Timing: [Any mentioned dates, times, durations]
        - Participants: [Expected attendees, roles mentioned]
        - Actions Required: [Required responses, confirmations, etc.]

        PRIORITY ASSESSMENT:
        - Urgency Level: [High/Medium/Low]
        - Response Needed: [Yes/No]
        - Timeline Requirements: [Any deadlines or time-sensitive elements]

        ANALYSIS SUMMARY:
        [2-3 sentences summarizing the key points and required actions]

        Be specific and detailed in your analysis while maintaining this structure.
        """

    async def analyze_email(self, email_content: str) -> Tuple[str, Dict[str, Any]]:
        """
        Perform deep email analysis with robust error handling.
        
        Conducts comprehensive content analysis while maintaining detailed
        logging and error handling capabilities. Returns analysis in a format
        suitable for LlamaAnalyzer processing.
        
        Args:
            email_content: Raw email content to analyze
            
        Returns:
            Tuple containing analysis text and metadata
        """
        if not self._validate_email_content(email_content):
            logger.error("Invalid or empty email content provided")
            return self._format_analysis_result(
                "Invalid email content provided",
                {"error": "Empty or invalid content"}
            )

        try:
            async with aiohttp.ClientSession() as session:
                request_payload = {
                    "model": self.config["model"]["name"],
                    "messages": [{
                        "role": "user",
                        "content": self._construct_prompt(email_content)
                    }],
                    "temperature": self.config["model"]["temperature"],
                    "max_tokens": self.config["model"]["max_tokens"]
                }
                
                logger.debug(f"Request payload: {request_payload}")

                async with session.post(
                    f"{self.api_endpoint}/chat/completions",
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {self.api_key}"
                    },
                    json=request_payload
                ) as response:
                    response_text = await response.text()
                    logger.debug(f"Raw API response: {response_text}")

                    if response.status != 200:
                        raise Exception(f"API request failed with status {response.status}: {response_text}")

                    result = await response.json()
                    content = result["choices"][0]["message"]["content"]
                    
                    return content, {
                        "source": "deepseek",
                        "model": self.config["model"]["name"],
                        "raw_response": content
                    }

        except Exception as e:
            logger.error(f"Error in DeepseekAnalyzer: {str(e)}", exc_info=True)
            return str(e), {"error": str(e)}

    def _format_analysis_result(self, content: str, metadata: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        """
        Format analysis results with consistent structure.
        
        Ensures analysis output maintains consistent format for LlamaAnalyzer
        processing while preserving all relevant metadata.
        
        Args:
            content: Analysis content
            metadata: Additional analysis metadata
            
        Returns:
            Tuple containing formatted content and metadata
        """
        return content, {
            "source": "deepseek",
            "timestamp": self._get_timestamp(),
            "metadata": metadata
        }

    def _get_timestamp(self) -> str:
        """Generate ISO format timestamp for analysis tracking."""
        return datetime.now().isoformat()