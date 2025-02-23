"""
Llama Response Categorizer for Email Classification

This module implements the final categorization stage of the email analysis pipeline,
taking detailed Deepseek analysis results and determining the appropriate handling
category through structured decision making.

Key Features:
- Processes natural language analysis into structured decisions
- Implements comprehensive categorization logic
- Provides detailed reasoning for decisions
- Maintains robust error handling
"""

import logging
from typing import Dict, Tuple, Any, Optional
from datetime import datetime
from integrations.groq.client_wrapper import EnhancedGroqClient
from config.analyzer_config import ANALYZER_CONFIG

logger = logging.getLogger(__name__)

class LlamaCategorizer:
    """
    Final-stage email categorizer using the Llama model.
    
    Processes detailed analysis results to make structured decisions
    about email handling categories. Implements comprehensive decision
    making with detailed reasoning and confidence scoring.
    """
    
    def __init__(self):
        """
        Initialize categorizer with required components.
        
        Sets up:
        - Groq client for API interaction
        - Model configuration
        - Logging infrastructure
        """
        self.client = EnhancedGroqClient()
        self.model_config = ANALYZER_CONFIG["default_analyzer"]["model"]
        
    async def categorize_email(
        self,
        initial_classification: str,
        deepseek_analysis: Dict[str, Any]
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Determine final email category based on comprehensive analysis.
        
        Takes the initial classification and detailed Deepseek analysis
        to make a final determination about email handling category.
        
        Args:
            initial_classification: Result from initial classification
            deepseek_analysis: Structured analysis from Deepseek
            
        Returns:
            Tuple containing (category, detailed_result)
        """
        try:
            # Construct decision prompt
            prompt = self._construct_decision_prompt(
                initial_classification,
                deepseek_analysis
            )
            
            # Process with Llama
            response = await self.client.process_with_retry(
                messages=[{"role": "user", "content": prompt}],
                model=self.model_config["name"],
                temperature=self.model_config["temperature"],
                max_completion_tokens=self.model_config["max_tokens"],
            )
            
            # Parse and validate decision
            decision_result = self._parse_decision_response(
                response.choices[0].message.content
            )
            
            logger.info("Successfully determined email category")
            return decision_result["category"], decision_result
            
        except Exception as e:
            logger.error(f"Error in categorization: {e}", exc_info=True)
            return "needs_review", self._get_error_decision(str(e))
            
    def _construct_decision_prompt(
        self,
        initial_classification: str,
        analysis: Dict[str, Any]
    ) -> str:
        """
        Construct optimized decision prompt.
        
        Creates a carefully engineered prompt that encourages structured
        decision making based on the provided analysis.
        """
        return f"""
        Determine the appropriate handling category for this email based on the following analysis:

        Initial Classification: {initial_classification}

        Deepseek Analysis:
        {self._format_analysis_sections(analysis)}

        Categorize this email into one of these categories:
        1. "standard_response": Clear meeting request with complete information
        2. "needs_review": Complex request or missing critical information
        3. "ignore": Not meeting related or no action needed

        Provide your decision in this exact JSON format:
        {{
            "category": "standard_response" or "needs_review" or "ignore",
            "confidence": float between 0 and 1,
            "reasoning": "Detailed explanation of the decision",
            "missing_information": ["list", "of", "missing", "details"] or [],
            "key_factors": ["list", "of", "decision", "factors"]
        }}
        """
            
    def _format_analysis_sections(self, analysis: Dict[str, Any]) -> str:
        """Format analysis sections for prompt inclusion."""
        sections = analysis.get("sections", {})
        return "\n\n".join([
            f"Meeting Characteristics:\n{sections.get('characteristics', 'Not available')}",
            f"Complexity Assessment:\n{sections.get('complexity', 'Not available')}",
            f"Suggested Handling:\n{sections.get('handling', 'Not available')}",
            f"Analysis Summary:\n{sections.get('summary', 'Not available')}"
        ])
            
    def _parse_decision_response(self, response: str) -> Dict[str, Any]:
        """
        Parse and validate decision response.
        
        Implements comprehensive parsing with:
        - JSON validation
        - Schema enforcement
        - Type checking
        - Default value handling
        """
        try:
            import json
            result = json.loads(response)
            
            # Validate category
            category = result.get("category", "needs_review").lower()
            if category not in ["standard_response", "needs_review", "ignore"]:
                logger.warning(f"Invalid category: {category}, defaulting to needs_review")
                category = "needs_review"
                
            # Construct validated response
            return {
                "category": category,
                "confidence": float(result.get("confidence", 0.0)),
                "reasoning": str(result.get("reasoning", "")),
                "missing_information": list(result.get("missing_information", [])),
                "key_factors": list(result.get("key_factors", [])),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error parsing decision response: {e}")
            return self._get_error_decision(str(e))
            
    def _get_error_decision(self, error: str) -> Dict[str, Any]:
        """Provide structured error response for failed decisions."""
        return {
            "category": "needs_review",
            "confidence": 0.0,
            "reasoning": f"Decision failed: {error}",
            "missing_information": [],
            "key_factors": [],
            "timestamp": datetime.now().isoformat(),
            "error": error
        }