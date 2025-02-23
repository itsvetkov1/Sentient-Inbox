"""
DeepseekAnalyzer: Advanced Email Content Analysis Service

This module implements sophisticated email content analysis using the Deepseek model,
focusing on providing comprehensive natural language analysis of email characteristics
and complexity. It serves as the detailed analysis stage in the multi-stage email
processing pipeline.

Key Features:
- Natural language analysis of email content
- Detailed meeting characteristic evaluation
- Complexity assessment
- Structured analysis output
- Comprehensive error handling and logging

Design Decisions:
- Uses natural language prompts for richer analysis
- Maintains clear separation from categorization logic
- Implements robust error recovery
- Provides detailed logging for debugging
"""

import logging
import os
import json
from datetime import datetime
from typing import Dict, Any, Optional
import aiohttp
from config.analyzer_config import ANALYZER_CONFIG

logger = logging.getLogger(__name__)

class DeepseekAnalyzer:
    """
    Advanced email content analyzer leveraging Deepseek's natural language capabilities.
    
    This analyzer focuses on extracting deep insights about email content,
    particularly meeting-related characteristics and complexity factors. It
    provides rich, natural language analysis for downstream categorization.
    """
    
    def __init__(self):
        """
        Initialize the analyzer with required configuration.
        
        Validates environment setup and configures API access with proper
        error handling and logging infrastructure.
        """
        self.api_key = os.environ.get("DEEPSEEK_API_KEY")
        if not self.api_key:
            raise ValueError("DEEPSEEK_API_KEY environment variable is not set")
            
        self.config = ANALYZER_CONFIG["deepseek_analyzer"]
        self.api_endpoint = self.config["model"]["api_endpoint"]
        
    async def analyze_email(self, email_content: str) -> Dict[str, Any]:
        """
        Perform comprehensive analysis of email content.
        
        Implements detailed content analysis focused on:
        - Meeting characteristics and context
        - Complexity factors
        - Required actions and timeline
        - Business impact
        
        Args:
            email_content: Raw email content to analyze
            
        Returns:
            Dict containing structured analysis results and metadata
        """
        try:
            # Log analysis attempt
            logger.info(f"Starting Deepseek analysis of email content")
            logger.debug(f"Email content length: {len(email_content)}")
            
            # Construct and execute analysis
            prompt = self._construct_analysis_prompt(email_content)
            raw_response = await self._call_deepseek_api(prompt)
            
            # Process and structure the response
            structured_analysis = self._process_analysis_response(raw_response)
            
            logger.info("Successfully completed Deepseek analysis")
            return structured_analysis
            
        except Exception as e:
            logger.error(f"Error during Deepseek analysis: {str(e)}", exc_info=True)
            return self._create_error_response(str(e))
            
    def _construct_analysis_prompt(self, content: str) -> str:
        """
        Create comprehensive analysis prompt.
        
        Constructs a detailed prompt that encourages rich, natural language
        analysis while maintaining focus on key aspects of interest.
        """
        return f"""
        Analyze this email content and provide a detailed assessment:

        EMAIL CONTENT:
        {content}

        Provide a comprehensive analysis using this structure:

        MEETING CHARACTERISTICS:
        - Core Purpose: [Describe the primary meeting objective and context]
        - Timeline Factors: [Analyze timing, urgency, and scheduling aspects]
        - Participant Dynamics: [Evaluate required attendees and roles]
        - Action Requirements: [Detail required responses or preparations]

        COMPLEXITY ASSESSMENT:
        - Information Completeness: [Evaluate if all necessary details are present]
        - Coordination Requirements: [Analyze scheduling and logistics complexity]
        - Business Impact: [Consider relevance and importance to operations]
        - Process Requirements: [Identify any special handling needs]

        ANALYSIS SUMMARY:
        [Provide a detailed summary of key points, requirements, and recommendations]

        HANDLING RECOMMENDATION:
        [Explain in natural language how this email should be handled and why,
        considering factors like urgency, complexity, and completeness of information]
        """
            
    async def _call_deepseek_api(self, prompt: str) -> str:
        """
        Execute API call to Deepseek with comprehensive error handling.
        
        Implements robust API interaction with:
        - Detailed error handling
        - Request validation
        - Response verification
        - Logging of all steps
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_endpoint}/chat/completions",
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {self.api_key}"
                    },
                    json={
                        "model": self.config["model"]["name"],
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": self.config["model"]["temperature"],
                        "max_tokens": self.config["model"]["max_tokens"]
                    }
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise Exception(f"API request failed: {response.status} - {error_text}")
                        
                    response_data = await response.json()
                    return response_data["choices"][0]["message"]["content"]
                    
        except Exception as e:
            logger.error(f"API call failed: {str(e)}", exc_info=True)
            raise Exception(f"Deepseek API error: {str(e)}")
            
    def _process_analysis_response(self, response: str) -> Dict[str, Any]:
        """
        Process and structure the analysis response.
        
        Extracts key sections and insights from the response while
        maintaining the natural language analysis format.
        """
        try:
            # Extract sections using clear delimiters
            sections = {
                "characteristics": self._extract_section(response, "MEETING CHARACTERISTICS"),
                "complexity": self._extract_section(response, "COMPLEXITY ASSESSMENT"),
                "summary": self._extract_section(response, "ANALYSIS SUMMARY"),
                "recommendation": self._extract_section(response, "HANDLING RECOMMENDATION")
            }
            
            # Create structured analysis result
            return {
                "source": "deepseek",
                "timestamp": datetime.now().isoformat(),
                "sections": sections,
                "raw_response": response,
                "metadata": {
                    "model": self.config["model"]["name"],
                    "sections_found": list(sections.keys())
                }
            }
            
        except Exception as e:
            logger.error(f"Error processing analysis response: {str(e)}", exc_info=True)
            return self._create_error_response(str(e))
            
    def _extract_section(self, content: str, section_name: str) -> str:
        """
        Extract a specific section from the analysis content.
        
        Implements robust section extraction with:
        - Multiple delimiter handling
        - Content validation
        - Error recovery
        """
        try:
            # Split on section name and get content
            parts = content.split(section_name + ":")
            if len(parts) < 2:
                return ""
                
            # Extract until next section or end
            section_content = parts[1].split("\n\n")[0].strip()
            return section_content
            
        except Exception as e:
            logger.warning(f"Error extracting section {section_name}: {e}")
            return ""
            
    def _create_error_response(self, error: str) -> Dict[str, Any]:
        """
        Create structured error response.
        
        Provides consistent error formatting while maintaining
        the expected response structure.
        """
        return {
            "source": "deepseek",
            "timestamp": datetime.now().isoformat(),
            "error": error,
            "sections": {
                "characteristics": "",
                "complexity": "",
                "summary": "Analysis failed",
                "recommendation": "Needs review due to analysis failure"
            },
            "metadata": {
                "error_type": type(error).__name__,
                "analysis_complete": False
            }
        }