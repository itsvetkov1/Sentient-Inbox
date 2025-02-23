"""
LlamaAnalyzer: AI-powered Email Analysis Service

This module implements sophisticated email content analysis using the llama-3.3-70b-versatile model.
It provides comprehensive email understanding through multi-stage analysis, content preprocessing,
and structured decision making.

Key Features:
- Intelligent content preprocessing to handle token limits
- Robust JSON response parsing and validation
- Comprehensive error handling and logging
- Integration with DeepSeek for enhanced analysis

Design Decisions:
- Implements content chunking for large emails
- Uses structured JSON for model responses
- Maintains detailed processing metrics
- Provides fallback analysis paths
"""

import logging
from typing import Dict, Tuple, Any, Optional, List
import json
from dataclasses import dataclass
from email_processing.classification.classifier import EmailTopic
from integrations.groq.client_wrapper import EnhancedGroqClient
from config.analyzer_config import ANALYZER_CONFIG

logger = logging.getLogger(__name__)

@dataclass
class AnalysisResult:
    """
    Structured container for email analysis results.
    
    Provides type-safe access to analysis components and
    maintains analysis metadata for debugging and monitoring.
    """
    key_points: List[str]
    sentiment: str
    urgency: str
    action_items: List[str]
    relevance: str
    confidence: float
    processing_metadata: Dict[str, Any]

class ContentChunker:
    """
    Handles intelligent content chunking for large emails.
    
    Implements sophisticated content splitting while preserving
    context and maintaining content coherence.
    """
    
    def __init__(self, max_tokens: int = 4000):
        self.max_tokens = max_tokens
        
    def chunk_content(self, content: str) -> List[str]:
        """Split content into processable chunks while preserving context."""
        # Rough token estimation (words as proxy)
        words = content.split()
        if len(words) <= self.max_tokens:
            return [content]
            
        chunks = []
        current_chunk = []
        current_length = 0
        
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        
        for paragraph in paragraphs:
            paragraph_length = len(paragraph.split())
            
            if current_length + paragraph_length > self.max_tokens:
                if current_chunk:
                    chunks.append('\n\n'.join(current_chunk))
                current_chunk = [paragraph]
                current_length = paragraph_length
            else:
                current_chunk.append(paragraph)
                current_length += paragraph_length
                
        if current_chunk:
            chunks.append('\n\n'.join(current_chunk))
            
        return chunks

class LlamaAnalyzer:
    """AI-powered email analysis service using the llama-3.3-70b-versatile model."""
    
    def __init__(self):
        """Initialize the analyzer with required components."""
        self.client = EnhancedGroqClient()
        self.model_config = ANALYZER_CONFIG["default_analyzer"]["model"]
        self.content_chunker = ContentChunker(
            max_tokens=self.model_config.get("max_input_tokens", 4000)
        )

    def _construct_classification_prompt(
        self,
        subject: str,
        content: str,
        sender: str,
        email_type: EmailTopic
    ) -> str:
        """Construct prompt for initial email classification."""
        return f"""Analyze this email to determine if it's meeting-related.

Email Details:
Subject: {subject}
From: {sender}
Content: {content}

Consider:
1. Explicit meeting mentions
2. Scheduling language
3. Time/date references
4. Location references
5. Coordination language

Provide response in JSON format:
{{
    "classification": "meeting_related" or "not_meeting",
    "confidence": float between 0 and 1,
    "reasoning": "brief explanation",
    "key_indicators": ["list", "of", "meeting", "related", "phrases"]
}}"""

    def _parse_classification_response(self, response: str) -> Dict[str, Any]:
        """Parse and validate classification response."""
        try:
            # Validate response is not empty
            if not response or not response.strip():
                raise ValueError("Empty response from API")
                
            # Handle potential brotli/gzip encoding
            if isinstance(response, bytes):
                try:
                    import brotli
                    response = brotli.decompress(response).decode('utf-8')
                except ImportError:
                    response = response.decode('utf-8')
                except Exception as e:
                    logger.error(f"Failed to decompress response: {str(e)}")
                    raise ValueError(f"Failed to decompress response: {str(e)}")

            # Clean response string
            response = response.strip()
            if not response.startswith('{'):
                # Extract JSON if wrapped in other content
                import re
                json_match = re.search(r'\{.*\}', response, re.DOTALL)
                if json_match:
                    response = json_match.group(0)
                else:
                    raise ValueError(f"No JSON object found in response: {response[:100]}...")

            # Parse JSON
            parsed = json.loads(response)
            
            # Validate required fields
            if "classification" not in parsed:
                raise ValueError(f"Missing classification field in response: {response[:100]}...")
            
            # Normalize classification value
            classification = parsed["classification"].lower()
            if classification not in ["meeting_related", "not_meeting"]:
                raise ValueError(f"Invalid classification value: {classification}")
            
            # Ensure all required fields with defaults
            result = {
                "classification": classification,
                "confidence": float(parsed.get("confidence", 0.0)),
                "reasoning": str(parsed.get("reasoning", "")),
                "key_indicators": list(parsed.get("key_indicators", []))
            }
            
            logger.debug(f"Successfully parsed classification response: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Classification response parsing failed: {str(e)}\nResponse: {response[:200]}...")
            return {
                "classification": "not_meeting",
                "confidence": 0.0,
                "reasoning": f"parsing failed: {str(e)}",
                "key_indicators": []
            }

    def _construct_decision_prompt(
        self,
        initial_classification: str,
        deepseek_decision: Optional[str],
        analysis: Dict
    ) -> str:
        """Construct prompt for final decision making."""
        return f"""Make a final decision about email handling based on multiple analyses.

Initial Classification: {initial_classification}
DeepSeek Decision: {deepseek_decision if deepseek_decision else 'Not Available'}

Detailed Analysis:
{json.dumps(analysis, indent=2)}

Determine the final handling category:
1. "standard_response": Clear meeting request, all details present
2. "needs_review": Complex or unclear request, missing details
3. "ignore": Not meeting related or no action needed

Provide response in JSON format:
{{
    "decision": "standard_response" or "needs_review" or "ignore",
    "confidence": float between 0 and 1,
    "reasoning": "explanation of decision",
    "requires_attention": boolean,
    "missing_details": ["list", "of", "missing", "information"]
}}"""

    def _parse_decision_response(self, response: str) -> Dict[str, Any]:
        """Parse and validate decision response."""
        try:
            parsed = json.loads(response)
            
            # Validate decision value
            decision = parsed.get("decision", "needs_review").lower()
            if decision not in ["standard_response", "needs_review", "ignore"]:
                raise ValueError(f"Invalid decision value: {decision}")
            
            return {
                "decision": decision,
                "confidence": float(parsed.get("confidence", 0.0)),
                "reasoning": str(parsed.get("reasoning", "")),
                "requires_attention": bool(parsed.get("requires_attention", True)),
                "missing_details": list(parsed.get("missing_details", []))
            }
            
        except Exception as e:
            logger.error(f"Decision response parsing failed: {str(e)}")
            return {
                "decision": "needs_review",
                "confidence": 0.0,
                "reasoning": "parsing failed",
                "requires_attention": True,
                "missing_details": []
            }

    async def classify_email(
    self,
    message_id: str,
    subject: str,
    content: str,
    sender: str,
    email_type: EmailTopic,
) -> Tuple[str, Dict]:
    # """
    # Perform initial classification of the email (Stage 1) with enhanced error handling.
    
    # Args:
    #     message_id: Unique email identifier
    #     subject: Email subject line
    #     content: Email body content
    #     sender: Email sender address
    #     email_type: Classification of email type
        
    # Returns:
    #     Tuple containing (initial_classification, initial_analysis)
    # """
        try:
            prompt = self._construct_classification_prompt(subject, content, sender, email_type)
            
            # Process with Groq API
            response = await self.client.process_with_retry(
                messages=[{"role": "user", "content": prompt}],
                model=self.model_config["name"],
                temperature=self.model_config["temperature"],
                max_completion_tokens=self.model_config["max_tokens"],
            )
            
            # Extract and process response content
            response_content = self._process_groq_response(response)
            classification_result = self._parse_classification_response(response_content)
            
            logger.info(f"Completed initial classification for {message_id}")
            logger.debug(f"Classification result: {classification_result}")
            
            return classification_result["classification"], classification_result
            
        except Exception as e:
            logger.error(f"Error in initial classification for email {message_id}: {str(e)}", exc_info=True)
            default_result = self._get_default_classification()
            return "needs_review", {
                "error": str(e),
                "processing_metadata": {"error_type": type(e).__name__},
                **default_result
            }

    async def analyze_email(
        self,
        message_id: str,
        subject: str,
        content: str,
        sender: str,
        email_type: EmailTopic,
    ) -> Dict:
        """Perform detailed content analysis of the email (Stage 2)."""
        try:
            content_chunks = self.content_chunker.chunk_content(content)
            chunk_analyses = []
            
            for chunk_idx, chunk in enumerate(content_chunks):
                try:
                    prompt = self._construct_prompt(
                        subject=subject,
                        content=chunk,
                        sender=sender,
                        email_type=email_type,
                        is_chunk=len(content_chunks) > 1,
                        chunk_index=chunk_idx
                    )
                    
                    response = await self.client.process_with_retry(
                        messages=[{"role": "user", "content": prompt}],
                        model=self.model_config["name"],
                        temperature=self.model_config["temperature"],
                        max_completion_tokens=self.model_config["max_tokens"],
                    )
                    
                    chunk_analysis = self._parse_response(response.choices[0].message.content)
                    chunk_analyses.append(chunk_analysis)
                    
                except Exception as e:
                    logger.error(f"Error analyzing chunk {chunk_idx}: {str(e)}")
                    continue
                    
            consolidated_analysis = self._consolidate_analyses(chunk_analyses)
            
            logger.info(f"Completed detailed analysis for {message_id} with {len(content_chunks)} chunks")
            
            return {
                **consolidated_analysis,
                "processing_metadata": {
                    "chunks_processed": len(content_chunks),
                    "successful_chunks": len(chunk_analyses),
                    "total_chunks": len(content_chunks)
                }
            }
            
        except Exception as e:
            logger.error(f"Error in detailed analysis for email {message_id}: {str(e)}", exc_info=True)
            return {
                "error": str(e),
                "processing_metadata": {"error_type": type(e).__name__}
            }

    async def make_decision(
        self,
        initial_classification: str,
        deepseek_decision: Optional[str],
        analysis: Dict
    ) -> Tuple[str, Dict]:
        """Make final decision based on all analyses (Stage 3)."""
        try:
            prompt = self._construct_decision_prompt(initial_classification, deepseek_decision, analysis)
            
            response = await self.client.process_with_retry(
                messages=[{"role": "user", "content": prompt}],
                model=self.model_config["name"],
                temperature=self.model_config["temperature"],
                max_completion_tokens=self.model_config["max_tokens"],
            )
            
            decision_result = self._parse_decision_response(response.choices[0].message.content)
            
            logger.info(f"Completed final decision making")
            
            return decision_result["decision"], decision_result
            
        except Exception as e:
            logger.error(f"Error in final decision making: {str(e)}", exc_info=True)
            return "needs_review", {
                "error": str(e),
                "processing_metadata": {"error_type": type(e).__name__}
            }

    def _construct_prompt(
        self,
        subject: str,
        content: str,
        sender: str,
        email_type: EmailTopic,
        is_chunk: bool = False,
        chunk_index: int = 0
    ) -> str:
        """Construct optimized analysis prompt with comprehensive context."""
        chunk_context = ""
        if is_chunk:
            chunk_context = f"\nNote: This is part {chunk_index + 1} of a longer email. Please analyze this section independently."
            
        return f"""
        Analyze the following email{' section' if is_chunk else ''}:

        Subject: {subject}
        From: {sender}
        Type: {email_type.value}{chunk_context}

        Content:
        {content}

        Provide a detailed analysis including:
        1. Key points of the email
        2. Sentiment analysis
        3. Urgency level
        4. Any action items or requests
        5. Relevance to the recipient's role or organization

        Format your response as a valid JSON object with these keys:
        {{
            "key_points": [],
            "sentiment": "",
            "urgency": "",
            "action_items": [],
            "relevance": ""
        }}
        
        Requirements:
        - Response MUST be valid JSON
        - Lists should be non-null arrays
        - Strings should be non-null
        - Use explicit values for sentiment and urgency
        """

    def _parse_response(self, response: str) -> Dict:
        """Parse and validate model response with comprehensive error handling."""
        try:
            # Attempt JSON parsing
            parsed = json.loads(response)
            
            # Validate required fields with default values
            required_fields = {
                "key_points": [],
                "sentiment": "",
                "urgency": "",
                "action_items": [],
                "relevance": ""
            }
            
            # Ensure all required fields exist with correct types
            validated = {}
            for field, default in required_fields.items():
                value = parsed.get(field, default)
                
                # Type validation and conversion
                if isinstance(default, list):
                    validated[field] = list(value) if isinstance(value, (list, tuple)) else []
                else:
                    validated[field] = str(value) if value else ""
                    
            return validated
            
        except json.JSONDecodeError as e:
            logger.warning(f"Response parsing failed: {str(e)}")
            return {field: default for field, default in required_fields.items()}
            
    def _consolidate_analyses(self, analyses: List[Dict]) -> Dict:
        """Consolidate multiple chunk analyses into a coherent result."""
        if not analyses:
            return {
                "key_points": [],
                "sentiment": "",
                "urgency": "",
                "action_items": [],
                "relevance": ""
            }
            
        consolidated = {
            "key_points": [],
            "action_items": [],
            "sentiment": analyses[0]["sentiment"],  # Use first chunk's sentiment
            "urgency": max(a["urgency"] for a in analyses) if analyses else "",  # Use highest urgency
            "relevance": analyses[0]["relevance"]  # Use first chunk's relevance
        }
        
        # Merge lists while removing duplicates
        seen_points = set()
        seen_actions = set()
        
        for analysis in analyses:
            for point in analysis.get("key_points", []):
                if point and point not in seen_points:
                    consolidated["key_points"].append(point)
                    seen_points.add(point)
                    
            for action in analysis.get("action_items", []):
                if action and action not in seen_actions:
                    consolidated["action_items"].append(action)
                    seen_actions.add(action)
                    
        return consolidated

    def _process_groq_response(self, response) -> str:
        """Process and extract content from Groq API response."""
        try:
            if not response or not hasattr(response, 'choices') or not response.choices:
                raise ValueError("Invalid response structure from Groq API")
                
            content = response.choices[0].message.content
            if not content:
                raise ValueError("Empty content in Groq API response")
                
            return content.strip()
            
        except Exception as e:
            logger.error(f"Error processing Groq response: {str(e)}")
            raise ValueError(f"Failed to process Groq response: {str(e)}")

    def _get_default_classification(self) -> Dict[str, Any]:
        """Get default classification result for error cases."""
        return {
            "classification": "needs_review",
            "confidence": 0.0,
            "reasoning": "error in classification",
            "key_indicators": []
        }
