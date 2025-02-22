"""
Content preprocessing module for email analysis pipeline.

This module implements sophisticated content preprocessing capabilities
for handling email content before model analysis. It manages token limits,
content cleaning, and information extraction while preserving critical 
context for analysis.

Design Decisions:
- Modular architecture for extensibility
- Configurable processing parameters
- Comprehensive content cleaning and normalization
- Intelligent information extraction
"""

from typing import Dict, Optional, List, Tuple
from bs4 import BeautifulSoup
import re
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class ProcessedContent:
    """Structured container for processed content results."""
    content: str
    metadata: Dict[str, any]
    token_estimate: int
    processing_stats: Dict[str, any]

class ContentPreprocessor:
    """
    Manages email content preprocessing for model analysis.
    
    Implements sophisticated content processing including:
    - HTML cleaning and text extraction
    - Intelligent content summarization
    - Token limit enforcement
    - Information prioritization
    
    Design Considerations:
    - Maintains content integrity while reducing size
    - Preserves critical information for analysis
    - Handles multiple content formats (HTML, plain text)
    - Provides detailed processing metrics
    """
    
    def __init__(self, 
                 max_tokens: int = 4000,
                 preserve_patterns: Optional[List[str]] = None,
                 config: Optional[Dict] = None):
        """
        Initialize content preprocessor with configurable parameters.
        
        Args:
            max_tokens: Maximum allowed tokens for model input
            preserve_patterns: Regex patterns for critical content preservation
            config: Additional configuration parameters
        """
        self.max_tokens = max_tokens
        self.preserve_patterns = preserve_patterns or [
            r'meeting\s+at\s+\d{1,2}(?::\d{2})?\s*(?:am|pm)?',
            r'schedule.*meeting',
            r'discuss.*at\s+\d{1,2}(?::\d{2})?'
        ]
        self.config = config or {}
        
    def preprocess_content(self, content: str) -> ProcessedContent:
        """
        Process email content with comprehensive cleaning and optimization.
        
        Implements multi-stage processing:
        1. HTML cleaning and text extraction
        2. Critical information identification
        3. Content summarization
        4. Token limit enforcement
        
        Args:
            content: Raw email content
            
        Returns:
            ProcessedContent containing cleaned content and metadata
            
        Raises:
            ContentProcessingError: For unrecoverable processing errors
        """
        try:
            processing_stats = {"original_length": len(content)}
            
            # Clean HTML content
            cleaned_content = self._clean_html(content)
            processing_stats["cleaned_length"] = len(cleaned_content)
            
            # Extract critical information
            extracted_info = self._extract_key_information(cleaned_content)
            processing_stats["extraction_success"] = bool(extracted_info)
            
            # Enforce token limits
            final_content = self._enforce_token_limit(extracted_info)
            processing_stats["final_length"] = len(final_content)
            processing_stats["estimated_tokens"] = len(final_content.split())
            
            logger.debug(f"Content preprocessing completed: {processing_stats}")
            
            return ProcessedContent(
                content=final_content,
                metadata={"preserved_patterns": self._find_preserved_patterns(final_content)},
                token_estimate=processing_stats["estimated_tokens"],
                processing_stats=processing_stats
            )
            
        except Exception as e:
            logger.error(f"Content preprocessing failed: {str(e)}", exc_info=True)
            raise ContentProcessingError(f"Failed to process content: {str(e)}")
            
    def _clean_html(self, content: str) -> str:
        """
        Clean HTML content with robust parsing and text extraction.
        
        Implements:
        - HTML structure parsing
        - Text content extraction
        - Whitespace normalization
        - Special character handling
        """
        try:
            soup = BeautifulSoup(content, 'html.parser')
            # Remove script and style elements
            for element in soup(['script', 'style']):
                element.decompose()
                
            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            return text
            
        except Exception as e:
            logger.warning(f"HTML cleaning failed, falling back to raw text: {str(e)}")
            return content

    def _extract_key_information(self, content: str) -> str:
        """
        Extract critical information with priority-based selection.
        
        Implements:
        - Pattern-based information extraction
        - Content relevance scoring
        - Priority-based selection
        """
        preserved_content = []
        
        # Preserve critical patterns
        for pattern in self.preserve_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            preserved_content.extend(matches)
            
        # Extract main content paragraphs
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        
        # Prioritize content
        prioritized = []
        if preserved_content:
            prioritized.extend(preserved_content)
        if paragraphs:
            prioritized.extend(paragraphs[:3])  # First 3 paragraphs
            
        return '\n\n'.join(prioritized)

    def _enforce_token_limit(self, content: str) -> str:
        """
        Ensure content meets token limits while preserving meaning.
        
        Implements:
        - Token estimation
        - Intelligent truncation
        - Content preservation
        """
        words = content.split()
        if len(words) <= self.max_tokens:
            return content
            
        preserved_indices = []
        # Find preserved pattern locations
        for pattern in self.preserve_patterns:
            for match in re.finditer(pattern, content, re.IGNORECASE):
                start_word = len(content[:match.start()].split())
                end_word = len(content[:match.end()].split())
                preserved_indices.extend(range(start_word, end_word))
                
        # Truncate while preserving critical content
        truncated_words = []
        for i, word in enumerate(words):
            if i < self.max_tokens or i in preserved_indices:
                truncated_words.append(word)
                
        return ' '.join(truncated_words)

class ContentProcessingError(Exception):
    """Custom exception for content processing errors."""
    pass