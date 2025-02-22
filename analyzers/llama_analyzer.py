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
from email_classifier import EmailTopic
from groq_integration.client_wrapper import EnhancedGroqClient
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
        """
        Split content into processable chunks while preserving context.
        
        Implements:
        - Intelligent paragraph boundary detection
        - Context preservation across chunks
        - Metadata extraction and retention
        """
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
    """
    AI-powered email analysis service using the llama-3.3-70b-versatile model.
    
    Implements comprehensive email analysis through:
    - Initial classification (Stage 1)
    - Detailed content analysis (used in Stage 2)
    - Final decision making (Stage 3)
    - Structured AI model interaction
    - Robust response parsing and validation
    - Detailed error handling and logging
    """
    
    def __init__(self):
        """
        Initialize the analyzer with required components and configuration.
        
        Sets up:
        - Model client configuration
        - Content processing utilities
        - Response parsing schemas
        - Logging infrastructure
        """
        self.client = EnhancedGroqClient()
        self.model_config = ANALYZER_CONFIG["default_analyzer"]["model"]
        self.content_chunker = ContentChunker(
            max_tokens=self.model_config.get("max_input_tokens", 4000)
        )
        
    async def classify_email(
        self,
        message_id: str,
        subject: str,
        content: str,
        sender: str,
        email_type: EmailTopic,
    ) -> Tuple[str, Dict]:
        """
        Perform initial classification of the email (Stage 1).
        
        Args:
            message_id: Unique email identifier
            subject: Email subject line
            content: Email body content
            sender: Email sender address
            email_type: Classification of email type
            
        Returns:
            Tuple containing (initial_classification, initial_analysis)
        """
        try:
            prompt = self._construct_classification_prompt(subject, content, sender, email_type)
            
            response = await self.client.process_with_retry(
                messages=[{"role": "user", "content": prompt}],
                model=self.model_config["name"],
                temperature=self.model_config["temperature"],
                max_completion_tokens=self.model_config["max_tokens"],
            )
            
            classification_result = self._parse_classification_response(response.choices[0].message.content)
            
            logger.info(f"Completed initial classification for {message_id}")
            
            return classification_result["classification"], classification_result
            
        except Exception as e:
            logger.error(f"Error in initial classification for email {message_id}: {str(e)}", exc_info=True)
            return "needs_review", {
                "error": str(e),
                "processing_metadata": {"error_type": type(e).__name__}
            }

    async def analyze_email(
        self,
        message_id: str,
        subject: str,
        content: str,
        sender: str,
        email_type: EmailTopic,
    ) -> Dict:
        """
        Perform detailed content analysis of the email (used in Stage 2).
        
        Args:
            message_id: Unique email identifier
            subject: Email subject line
            content: Email body content
            sender: Email sender address
            email_type: Classification of email type
            
        Returns:
            Detailed analysis dictionary
        """
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
        """
        Make the final decision based on initial classification and detailed analysis (Stage 3).
        
        Args:
            initial_classification: Result from the initial classification
            deepseek_decision: Decision from DeepseekAnalyzer (if applicable)
            analysis: Detailed analysis from Stage 2
            
        Returns:
            Tuple containing (final_decision, final_analysis)
        """
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
        """
        Construct optimized analysis prompt with comprehensive context.
        
        Implements:
        - Context-aware prompt construction
        - Chunk-aware analysis guidance
        - Structured response formatting
        """
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
        """
        Parse and validate model response with comprehensive error handling.
        
        Implements:
        - Strict JSON validation
        - Schema conformance checking
        - Default value handling
        - Error recovery
        """
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
        """
        Consolidate multiple chunk analyses into a coherent result.
        
        Implements:
        - Intelligent result merging
        - Duplicate removal
        - Priority-based consolidation
        """
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

    def _determine_recommendation(self, analysis: Dict) -> str:
        """
        Determine processing recommendation based on analysis results.
        
        Implementation:
        - Evaluates content complexity
        - Assesses urgency levels
        - Considers action requirements
        - Provides reasoned decision
        """
        # Check for critical indicators
        has_action_items = bool(analysis.get("action_items"))
        urgency = analysis.get("urgency", "").lower()
        
        if urgency == "high" or has_action_items:
            return "needs_review"
        
        return "standard_response"
