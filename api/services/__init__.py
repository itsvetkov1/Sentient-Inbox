"""
API Services Package

Centralizes service implementations for clean business logic
separation from route handlers.

Design Considerations:
- Clean separation from route handling
- Reusable business logic
- Proper dependency injection
"""

from api.services.email_service import EmailService, get_email_service

__all__ = ["EmailService", "get_email_service"]
