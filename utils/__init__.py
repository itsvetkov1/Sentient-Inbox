"""
Utility module initialization and exports.

This module provides centralized access to utility functions and services,
implementing comprehensive date handling, type conversion, validation, and
other cross-cutting concerns used throughout the email processing system.

Design Decisions:
- Centralized utility exports
- Clear function categorization
- Comprehensive type hints
- Extensive documentation

Architecture:
- Modular utility organization
- Consistent interface patterns
- Proper dependency management
- Future extensibility support
"""

from typing import Dict, List, Optional, Tuple, Union
from datetime import datetime

# Date handling utilities
from .date_utils import (
    parse_email_date,
    format_iso_date,
    is_valid_iso_date,
    DateParsingError
)

__all__ = [
    # Date handling exports
    'parse_email_date',
    'format_iso_date',
    'is_valid_iso_date',
    'DateParsingError',
]

# Version information
__version__ = '1.0.0'

# Module configuration
DEFAULT_CONFIG: Dict[str, Union[str, int, bool]] = {
    'default_timezone': 'UTC',
    'date_format_strict': True,
    'enable_debug_logging': False
}

def configure(config: Optional[Dict[str, Union[str, int, bool]]] = None) -> None:
    """
    Configure utility module behavior with comprehensive validation.
    
    Implements configuration management for utility functions,
    providing customization of default behaviors while maintaining
    proper validation and error handling.
    
    Args:
        config: Optional configuration dictionary to override defaults
    
    Raises:
        ValueError: If configuration validation fails
    """
    if config is not None:
        for key, value in config.items():
            if key in DEFAULT_CONFIG:
                DEFAULT_CONFIG[key] = value
            else:
                raise ValueError(f"Unknown configuration key: {key}")

def get_module_info() -> Dict[str, str]:
    """
    Get comprehensive module information for diagnostics.
    
    Returns detailed information about the utility module's
    configuration, version, and capabilities. Useful for
    debugging and system verification.
    
    Returns:
        Dictionary containing module information
    """
    return {
        'version': __version__,
        'config': str(DEFAULT_CONFIG),
        'available_utils': sorted(__all__),
        'python_version': platform.python_version(),
    }

# Initialize module configuration
configure()