class POMException(Exception):
    """Base exception class for POM project."""
    pass

class ResumeProcessingError(POMException):
    """Custom exception for resume processing errors."""
    pass
