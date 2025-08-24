"""
Custom exceptions for the application
"""

from typing import Any, Dict, Optional


class PomegranateException(Exception):
    """Base exception for Pomegranate application"""
    
    def __init__(
        self,
        message: str,
        error_code: str = "INTERNAL_ERROR",
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(PomegranateException):
    """Validation error exception"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            status_code=400,
            details=details
        )


class AuthenticationError(PomegranateException):
    """Authentication error exception"""
    
    def __init__(self, message: str = "Authentication failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="AUTHENTICATION_ERROR",
            status_code=401,
            details=details
        )


class AuthorizationError(PomegranateException):
    """Authorization error exception"""
    
    def __init__(self, message: str = "Access denied", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="AUTHORIZATION_ERROR",
            status_code=403,
            details=details
        )


class NotFoundError(PomegranateException):
    """Resource not found exception"""
    
    def __init__(self, resource: str, resource_id: Any, details: Optional[Dict[str, Any]] = None):
        message = f"{resource} with id {resource_id} not found"
        super().__init__(
            message=message,
            error_code="NOT_FOUND_ERROR",
            status_code=404,
            details=details
        )


class ConflictError(PomegranateException):
    """Resource conflict exception"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="CONFLICT_ERROR",
            status_code=409,
            details=details
        )


class RateLimitError(PomegranateException):
    """Rate limit exceeded exception"""
    
    def __init__(self, message: str = "Rate limit exceeded", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="RATE_LIMIT_ERROR",
            status_code=429,
            details=details
        )


class ExternalServiceError(PomegranateException):
    """External service error exception"""
    
    def __init__(self, service: str, message: str, details: Optional[Dict[str, Any]] = None):
        full_message = f"External service {service} error: {message}"
        super().__init__(
            message=full_message,
            error_code="EXTERNAL_SERVICE_ERROR",
            status_code=502,
            details=details
        )


class AIProcessingError(PomegranateException):
    """AI processing error exception"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="AI_PROCESSING_ERROR",
            status_code=500,
            details=details
        )


class FileUploadError(PomegranateException):
    """File upload error exception"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="FILE_UPLOAD_ERROR",
            status_code=400,
            details=details
        )


class DatabaseError(PomegranateException):
    """Database error exception"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="DATABASE_ERROR",
            status_code=500,
            details=details
        )