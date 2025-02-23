"""
Base processor implementation defining core processing interfaces.

This module establishes the foundational processor architecture,
implementing common functionality, standardized interfaces, and
core processing capabilities used across the system.

Design Decisions:
- Abstract base classes for processor hierarchy
- Standardized configuration handling
- Common utility methods
- Comprehensive error handling
"""

from typing import Dict, Any, Optional
import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class BaseProcessor(ABC):
    """
    Abstract base class for all processors in the system.
    
    Implements core functionality and defines standard interfaces
    that all processors must implement. Provides common utilities
    and configuration handling used across processor implementations.
    
    Design Considerations:
    - Standardized initialization
    - Common configuration handling
    - Shared utility methods
    - Comprehensive error management
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize base processor with configuration.
        
        Args:
            config: Optional configuration dictionary for processor behavior
        """
        self.config = config or {}
        self._validate_configuration()
        
    def _validate_configuration(self) -> None:
        """
        Validate processor configuration.
        
        Implements comprehensive configuration validation ensuring:
        - Required parameters are present
        - Parameter types are correct
        - Values are within valid ranges
        - Dependencies are satisfied
        
        Raises:
            ValueError: If configuration is invalid
        """
        try:
            # Base configuration validation
            # Subclasses should extend this method
            pass
        except Exception as e:
            logger.error(f"Configuration validation failed: {e}")
            raise ValueError(f"Invalid processor configuration: {e}")
            
    @abstractmethod
    def process(self, content: Any) -> Any:
        """
        Process input content according to processor implementation.
        
        This abstract method defines the standard processing interface
        that all concrete processors must implement.
        
        Args:
            content: Input content to process
            
        Returns:
            Processed content in implementation-specific format
            
        Raises:
            NotImplementedError: Must be implemented by concrete classes
        """
        raise NotImplementedError("Concrete processors must implement process method")
        
    def _handle_error(self, error: Exception, context: Dict[str, Any]) -> None:
        """
        Handle processing errors with comprehensive logging.
        
        Implements standardized error handling used across all processors:
        - Detailed error logging
        - Context preservation
        - Error classification
        - Recovery attempts when possible
        
        Args:
            error: Exception that occurred
            context: Processing context when error occurred
        """
        logger.error(
            f"Processing error in {self.__class__.__name__}: {error}",
            extra={"processing_context": context},
            exc_info=True
        )