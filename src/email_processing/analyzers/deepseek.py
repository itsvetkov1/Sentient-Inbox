"""
DeepseekAnalyzer: Comprehensive Email Content Analysis Service

Implements detailed analysis of meeting-related emails, providing natural
language summaries and handling recommendations for the final categorization
stage of the pipeline.

Design Considerations:
- Comprehensive DEBUG level logging throughout all operations
- Complete input/output capturing for model interactions
- Detailed error state documentation with full context preservation
- Processing flow monitoring with decision point tracking
- Performance metrics tracking for system monitoring
- Enhanced timeout handling for reliable API communication
"""

import logging
import os
import json
import traceback
import asyncio
import hashlib
from typing import Dict, Tuple, Optional, Any
from datetime import datetime
import aiohttp
from config.analyzer_config import ANALYZER_CONFIG

# Configure logger with proper naming
logger = logging.getLogger(__name__)

class DeepseekAnalyzer:
    """
    Detailed content analyzer using Deepseek model for comprehensive email understanding.
    
    Implements the second stage of the three-stage email analysis pipeline, providing
    rich natural language analysis of email content that has been identified as
    meeting-related in the first stage. Focuses on meeting characteristics, complexity,
    urgency, and identification of missing critical information.
    
    Features:
    - Comprehensive DEBUG level logging throughout all operations
    - Complete input/output tracking for API interactions
    - Detailed error state documentation with context preservation
    - Processing flow monitoring with decision tracking
    - Performance metrics collection for system monitoring
    - Enhanced timeout configurations for reliable API communication
    """
    
    def __init__(self):
        """
        Initialize analyzer with configuration and API setup.
        
        Loads configuration from the centralized analyzer configuration,
        sets up API endpoints, and verifies API key availability.
        
        Raises:
            ValueError: If the required DEEPSEEK_API_KEY environment variable is not set
        """
        self.config = ANALYZER_CONFIG["deepseek_analyzer"]
        self.api_endpoint = self.config["model"]["api_endpoint"]
        self.api_key = os.environ.get("DEEPSEEK_API_KEY")
        
        # Load timeout settings from config or use defaults
        self.timeout_seconds = self.config.get("timeout", 120)
        
        # Log initialization with configuration details (excluding sensitive data)
        logger.debug(
            f"DeepseekAnalyzer initialized with configuration: "
            f"model={self.config['model']['name']}, "
            f"endpoint={self.api_endpoint}, "
            f"temperature={self.config['model'].get('temperature', 0.7)}, "
            f"timeout={self.timeout_seconds}s"
        )
        
        if not self.api_key:
            logger.error("DEEPSEEK_API_KEY environment variable not set")
            raise ValueError("DEEPSEEK_API_KEY environment variable not set")
    
    async def analyze_email(self, email_content: str) -> Tuple[str, str, Optional[str]]:
        """
        Perform comprehensive analysis of email content.
        
        Implements detailed analysis of meeting-related email content, evaluating:
        - Meeting characteristics (purpose, timeline, participants)
        - Complexity factors (coordination needs, prerequisites)
        - Urgency level and time sensitivity
        - Missing critical information (date, time, location)
        - Required actions or preparations
        
        Args:
            email_content: Raw email content to analyze
            
        Returns:
            Tuple of (summary: str, recommendation: str, error: Optional[str])
            - summary: Detailed analysis of the email content
            - recommendation: Handling recommendation (standard_response, needs_review, ignore)
            - error: Error message if analysis failed, None otherwise
        """
        start_time = datetime.now()
        
        # Generate a request ID using hash of content and timestamp
        content_hash = hashlib.md5(email_content.encode()).hexdigest()[:6]
        request_id = f"deepseek-{start_time.strftime('%Y%m%d%H%M%S')}-{content_hash}"
        
        try:
            logger.info(f"[{request_id}] Starting detailed email content analysis")
            
            # Log input details at debug level
            logger.debug(
                f"[{request_id}] Analyzing content of length: {len(email_content)} characters\n"
                f"Content preview: {email_content[:100]}..." if len(email_content) > 100 else email_content
            )
            
            # Construct analysis prompt
            prompt = self._construct_analysis_prompt(email_content)
            logger.debug(f"[{request_id}] Analysis prompt generated with length: {len(prompt)}")
            
            # Prepare API request
            request_payload = {
                "model": self.config["model"]["name"],
                "messages": [{"role": "user", "content": prompt}],
                "temperature": self.config["model"].get("temperature", 0.7)
            }
            
            # Log API request configuration
            logger.debug(
                f"[{request_id}] Sending API request with configuration:\n"
                f"Model: {request_payload['model']}\n"
                f"Temperature: {request_payload['temperature']}\n"
                f"Message length: {len(prompt)}"
            )
            
            # Check if development fallback mode is enabled
            use_fallback = self.config.get("use_fallback", False)
            
            if use_fallback:
                # Development/testing mode with mock response
                logger.warning(f"[{request_id}] Using fallback mode for development/testing")
                await asyncio.sleep(0.5)  # Simulate processing time
                response = self._generate_mock_response(email_content)
            else:
                # Process with Deepseek API with detailed timing
                api_start_time = datetime.now()
                response = await self._make_api_request(request_id, request_payload)
                api_duration = (datetime.now() - api_start_time).total_seconds()
                logger.debug(f"[{request_id}] API request completed in {api_duration:.3f} seconds")
            
            # Extract analysis content
            analysis = response["choices"][0]["message"]["content"]
            
            # Log raw analysis result at DEBUG level
            logger.debug(f"[{request_id}] Raw analysis result:\n{analysis}")
            
            # Process analysis results
            processing_start = datetime.now()
            summary, recommendation = self._process_analysis(analysis, request_id)
            processing_duration = (datetime.now() - processing_start).total_seconds()
            
            # Calculate total processing time
            total_duration = (datetime.now() - start_time).total_seconds()
            
            # Log results and timing information
            logger.info(
                f"[{request_id}] Successfully completed detailed analysis in {total_duration:.3f} seconds"
            )
            logger.debug(
                f"[{request_id}] Analysis results:\n"
                f"Summary length: {len(summary)}\n"
                f"Recommendation: {recommendation}"
            )
            
            return summary, recommendation, None
            
        except Exception as e:
            # Capture full error context
            error_msg = f"Analysis failed: {str(e)}"
            stack_trace = traceback.format_exc()
            
            # Calculate error timing
            error_duration = (datetime.now() - start_time).total_seconds()
            
            # Log comprehensive error information
            logger.error(
                f"[{request_id}] {error_msg} after {error_duration:.3f} seconds\n"
                f"Stack trace:\n{stack_trace}"
            )
            
            # Use fallback for development or return error
            if self.config.get("use_fallback_on_error", True):
                logger.warning(f"[{request_id}] Using fallback analysis due to error")
                summary = self._generate_fallback_summary(email_content)
                return summary, "needs_review", error_msg
            else:
                return "", "needs_review", error_msg

    async def _make_api_request(self, request_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make API request to Deepseek API with comprehensive error handling.
        
        Implements detailed request handling with proper error recovery,
        retry logic, comprehensive logging, and enhanced timeout handling.
        
        Args:
            request_id: Unique identifier for tracking this request
            payload: Request payload containing model configuration and prompt
            
        Returns:
            Dictionary containing the API response
            
        Raises:
            Exception: If the API request fails after retry attempts
        """
        retry_count = 0
        max_retries = self.config.get("retry_count", 1) 
        retry_delay = self.config.get("retry_delay", 3)  # seconds
        
        # Important: Create a proper ClientTimeout object, not a dictionary
        # This fixes the "TypeError: '>' not supported between instances of 'dict' and 'int'" error
        timeout = aiohttp.ClientTimeout(total=self.timeout_seconds)
        
        logger.debug(f"[{request_id}] Configured API request with timeout: {self.timeout_seconds}s")
        
        while True:
            try:
                logger.debug(f"[{request_id}] API request attempt {retry_count + 1}/{max_retries + 1}")
                
                async with aiohttp.ClientSession(timeout=timeout) as session:
                    request_start_time = datetime.now()
                    
                    async with session.post(
                        f"{self.api_endpoint}/chat/completions",
                        headers={
                            "Content-Type": "application/json",
                            "Authorization": f"Bearer {self.api_key}"
                        },
                        json=payload
                    ) as response:
                        # Log response status
                        connection_time = (datetime.now() - request_start_time).total_seconds()
                        logger.debug(f"[{request_id}] API response status: {response.status} (connection time: {connection_time:.3f}s)")
                        
                        if response.status != 200:
                            response_text = await response.text()
                            logger.warning(
                                f"[{request_id}] API request failed with status {response.status}: "
                                f"{response_text[:500]}..."
                            )
                            raise Exception(f"API request failed: {response.status} - {response_text[:200]}")
                        
                        # Read response with explicit timeout handling
                        try:
                            # Use asyncio.wait_for to ensure we don't hang indefinitely
                            result = await asyncio.wait_for(
                                response.json(), 
                                timeout=self.timeout_seconds
                            )
                            
                            # Calculate total request time
                            total_request_time = (datetime.now() - request_start_time).total_seconds()
                            
                            # Log successful response
                            logger.debug(
                                f"[{request_id}] API request successful: received {len(json.dumps(result))} bytes "
                                f"in {total_request_time:.3f}s"
                            )
                            
                            return result
                            
                        except asyncio.TimeoutError:
                            logger.error(f"[{request_id}] Timeout while reading response body after {self.timeout_seconds}s")
                            raise TimeoutError(f"Timeout reading response body after {self.timeout_seconds}s")
            
            except asyncio.TimeoutError as e:
                # Explicit handling for timeout errors
                logger.warning(f"[{request_id}] Request timed out: {str(e)}")
                retry_count += 1
                if retry_count > max_retries:
                    logger.error(f"[{request_id}] Max retries exceeded after timeout")
                    raise TimeoutError(f"API request timed out after {max_retries+1} attempts")
                
                logger.warning(
                    f"[{request_id}] Retrying timed-out request (attempt {retry_count}/{max_retries}). "
                    f"Waiting {retry_delay} seconds..."
                )
                await asyncio.sleep(retry_delay)
                
            except Exception as e:
                retry_count += 1
                if retry_count > max_retries:
                    logger.error(f"[{request_id}] Max retries exceeded: {str(e)}")
                    raise
                
                logger.warning(
                    f"[{request_id}] API request failed (attempt {retry_count}/{max_retries}): {str(e)}. "
                    f"Retrying in {retry_delay} seconds..."
                )
                await asyncio.sleep(retry_delay)

    def _generate_mock_response(self, content: str) -> Dict[str, Any]:
        """
        Generate a mock response for development and testing.
        
        Creates a realistic response structure mimicking the Deepseek API
        for testing pipeline functionality when the API is unavailable.
        
        Args:
            content: Email content being analyzed
            
        Returns:
            Dictionary containing structured mock response
        """
        # Simple content-based analysis to generate a plausible mock response
        is_complex = len(content) > 500 or "discuss" in content.lower()
        has_date_time = any(term in content.lower() for term in ["tomorrow", "today", "am", "pm", ":00"])
        
        # Build appropriate mock content
        if is_complex:
            recommendation = "needs_review"
            summary = (
                "The email contains a complex meeting request with multiple components that require attention. "
                "It appears to involve coordination with several team members and has dependencies on "
                "other work items. The urgency level seems moderate to high."
            )
        elif has_date_time:
            recommendation = "standard_response"
            summary = (
                "This is a straightforward meeting request with clear date and time information. "
                "The purpose appears to be a simple discussion or update on a specific topic. "
                "All required information seems to be present."
            )
        else:
            recommendation = "ignore"
            summary = (
                "The content mentions a meeting but lacks specific details about timing or purpose. "
                "It appears to be informational rather than requiring a specific response or action."
            )
            
        # Create a structured mock response mimicking API format
        return {
            "id": f"mock-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "object": "chat.completion",
            "created": int(datetime.now().timestamp()),
            "model": "mock-deepseek-reasoner",
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": f"SUMMARY: {summary}\n\nRECOMMENDATION: {recommendation}"
                    },
                    "finish_reason": "stop"
                }
            ],
            "usage": {
                "prompt_tokens": len(content.split()),
                "completion_tokens": len(summary.split()) + 10,
                "total_tokens": len(content.split()) + len(summary.split()) + 10
            }
        }
    
    def _generate_fallback_summary(self, content: str) -> str:
        """
        Generate a fallback summary when API processing fails.
        
        Creates a basic analysis of the email content to ensure the pipeline
        can continue functioning even when the external API is unavailable.
        
        Args:
            content: Email content to analyze
            
        Returns:
            Basic summary of email content for pipeline continuation
        """
        # Extract basic meeting characteristics from content
        content_lower = content.lower()
        
        has_date = any(term in content_lower for term in ["tomorrow", "today", "monday", "tuesday", "wednesday", "thursday", "friday"])
        has_time = any(term in content_lower for term in [":00", "am", "pm", "morning", "afternoon"])
        has_location = any(term in content_lower for term in ["room", "office", "building", "cafe", "online", "zoom", "teams", "meet", "conference"])
        
        # Build appropriate fallback summary
        missing_items = []
        if not has_date:
            missing_items.append("date")
        if not has_time:
            missing_items.append("time")
        if not has_location:
            missing_items.append("location")
            
        if missing_items:
            missing_str = ", ".join(missing_items)
            summary = (
                f"This appears to be a meeting-related communication, but lacks clear specification of {missing_str}. "
                f"The email content is {len(content)} characters long and contains basic meeting discussion. "
                f"Due to the missing information, this email should be reviewed manually or additional information "
                f"should be requested."
            )
        else:
            summary = (
                f"This email appears to contain a meeting request with date, time, and location information. "
                f"The content is {len(content)} characters long and seems to be a straightforward meeting coordination. "
                f"A standard response confirming the meeting details would be appropriate."
            )
            
        return summary

    def _construct_analysis_prompt(self, content: str) -> str:
        """
        Construct comprehensive analysis prompt.
        
        Creates a prompt that encourages detailed analysis of meeting
        characteristics while maintaining focus on practical implications.
        The prompt is designed to elicit structured information about the
        meeting's purpose, complexity, urgency, and required actions.
        
        Args:
            content: Email content to analyze
            
        Returns:
            Formatted prompt optimized for detailed content analysis
        """
        # Use the configured system prompt if available, otherwise use default
        system_prompt = self.config.get("analysis", {}).get("system_prompt", "")
        
        prompt = f"""
        {system_prompt}
        
        Analyze this email content comprehensively:

        {content}

        Provide a concise summary covering:
        1. Meeting characteristics (purpose, timeline, participants)
        2. Complexity factors (coordination needs, prerequisites)
        3. Urgency level and time sensitivity
        4. Missing critical information (date, time, location)
        5. Required actions or preparations

        End your analysis with one of these recommendations:
        - 'standard_response' - For straightforward meetings needing only date/time/location confirmation
        - 'needs_review' - For complex or urgent meetings requiring additional action
        - 'ignore' - For non-actionable or irrelevant meeting mentions

        Format:
        SUMMARY: [Your detailed analysis]
        RECOMMENDATION: [Your chosen recommendation]
        """
        
        return prompt.strip()

    def _process_analysis(self, analysis: str, request_id: str) -> Tuple[str, str]:
        """
        Process and structure the analysis response.
        
        Extracts the summary and recommendation from the analysis while
        ensuring consistent formatting and completeness. Implements validation
        of the analysis structure and formats the output for downstream
        components in the pipeline.
        
        Args:
            analysis: Raw analysis text from the model
            request_id: Unique identifier for tracking this request
            
        Returns:
            Tuple of (summary: str, recommendation: str)
            - summary: Extracted and formatted summary section
            - recommendation: Validated recommendation (standard_response, needs_review, ignore)
        """
        try:
            logger.debug(f"[{request_id}] Processing analysis output of length: {len(analysis)}")
            
            # Check if format matches expected structure
            has_summary_tag = "SUMMARY:" in analysis
            has_recommendation_tag = "RECOMMENDATION:" in analysis
            
            logger.debug(
                f"[{request_id}] Analysis structure check: "
                f"has_summary_tag={has_summary_tag}, has_recommendation_tag={has_recommendation_tag}"
            )
            
            if not (has_summary_tag and has_recommendation_tag):
                logger.warning(
                    f"[{request_id}] Analysis format doesn't match expected structure. "
                    f"Using fallback processing approach."
                )
                
                # Attempt to extract using basic heuristics if standard format fails
                if "RECOMMENDATION:" in analysis:
                    parts = analysis.split("RECOMMENDATION:", 1)
                    summary = parts[0].replace("SUMMARY:", "").strip()
                    recommendation_text = parts[1].strip().lower()
                elif "\n\n" in analysis:
                    # Try to split on double newline if no explicit sections
                    parts = analysis.rsplit("\n\n", 1)
                    summary = parts[0].strip()
                    recommendation_text = parts[1].strip().lower()
                else:
                    # If all else fails, use the whole text as summary
                    summary = analysis.strip()
                    recommendation_text = ""
            else:
                # Standard processing when format matches expectations
                parts = analysis.split("RECOMMENDATION:", 1)
                summary = parts[0].replace("SUMMARY:", "").strip()
                recommendation_text = parts[1].strip().lower()
            
            # Extract and validate recommendation
            valid_recommendations = ["standard_response", "needs_review", "ignore"]
            
            # Find the closest matching recommendation
            recommendation = next(
                (r for r in valid_recommendations if r in recommendation_text),
                "needs_review"  # Default to needs_review if no valid recommendation found
            )
            
            logger.debug(
                f"[{request_id}] Extracted recommendation: '{recommendation}' "
                f"(extracted from: '{recommendation_text[:50]}...')"
            )
            
            if recommendation != recommendation_text:
                logger.info(
                    f"[{request_id}] Normalized recommendation from "
                    f"'{recommendation_text}' to '{recommendation}'"
                )
            
            return summary, recommendation
            
        except Exception as e:
            # Log exception with stack trace
            logger.error(
                f"[{request_id}] Error processing analysis: {str(e)}\n"
                f"Stack trace:\n{traceback.format_exc()}"
            )
            
            # Return safe defaults
            return "Analysis processing failed", "needs_review"