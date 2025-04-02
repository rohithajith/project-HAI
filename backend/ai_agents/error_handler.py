from typing import Dict, Any, Optional, Type, List
from pydantic import BaseModel, Field
from datetime import datetime
import logging
import traceback
from pathlib import Path
import json
import asyncio
from functools import wraps

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ErrorMetadata(BaseModel):
    """Schema for error metadata."""
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    agent_name: Optional[str] = None
    conversation_id: Optional[str] = None
    severity: str = Field(..., description="Error severity level")
    category: str = Field(..., description="Error category")
    retry_count: int = Field(default=0, description="Number of retry attempts")
    stack_trace: Optional[str] = None
    context: Dict[str, Any] = Field(default_factory=dict)

class ErrorResponse(BaseModel):
    """Schema for standardized error responses."""
    error_code: str = Field(..., description="Unique error code")
    message: str = Field(..., description="User-friendly error message")
    details: Optional[str] = None
    metadata: ErrorMetadata

# Custom Exceptions
class AgentError(Exception):
    """Base exception for all agent-related errors."""
    def __init__(self, 
                 message: str, 
                 error_code: str,
                 metadata: Optional[ErrorMetadata] = None):
        self.message = message
        self.error_code = error_code
        self.metadata = metadata or ErrorMetadata(
            severity="error",
            category="agent"
        )
        super().__init__(self.message)

class ContentFilterError(AgentError):
    """Exception for content filtering related errors."""
    def __init__(self, message: str, metadata: Optional[ErrorMetadata] = None):
        super().__init__(
            message=message,
            error_code="CONTENT_FILTER_ERROR",
            metadata=metadata or ErrorMetadata(
                severity="warning",
                category="content_filter"
            )
        )

class ProcessingError(AgentError):
    """Exception for message processing errors."""
    def __init__(self, message: str, metadata: Optional[ErrorMetadata] = None):
        super().__init__(
            message=message,
            error_code="PROCESSING_ERROR",
            metadata=metadata or ErrorMetadata(
                severity="error",
                category="processing"
            )
        )

class ValidationError(AgentError):
    """Exception for input validation errors."""
    def __init__(self, message: str, metadata: Optional[ErrorMetadata] = None):
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            metadata=metadata or ErrorMetadata(
                severity="warning",
                category="validation"
            )
        )

class AuthorizationError(AgentError):
    """Exception for authorization related errors."""
    def __init__(self, message: str, metadata: Optional[ErrorMetadata] = None):
        super().__init__(
            message=message,
            error_code="AUTHORIZATION_ERROR",
            metadata=metadata or ErrorMetadata(
                severity="error",
                category="authorization"
            )
        )

class RateLimitError(AgentError):
    """Exception for rate limiting."""
    def __init__(self, message: str, metadata: Optional[ErrorMetadata] = None):
        super().__init__(
            message=message,
            error_code="RATE_LIMIT_ERROR",
            metadata=metadata or ErrorMetadata(
                severity="warning",
                category="rate_limit"
            )
        )

class ErrorHandler:
    """Centralized error handling for the agent system."""
    
    def __init__(self):
        self.error_log_path = Path("logs/errors.log")
        self.error_log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Configure file handler
        file_handler = logging.FileHandler(self.error_log_path)
        file_handler.setLevel(logging.ERROR)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        # Error response templates
        self.response_templates = {
            "CONTENT_FILTER_ERROR": "I apologize, but I cannot process that request due to content restrictions.",
            "PROCESSING_ERROR": "I encountered an error processing your request. Please try again.",
            "VALIDATION_ERROR": "Please provide valid input for your request.",
            "AUTHORIZATION_ERROR": "You are not authorized to perform this action.",
            "RATE_LIMIT_ERROR": "Please wait a moment before making another request.",
            "DEFAULT": "An unexpected error occurred. Please try again later."
        }
        
        # Retry configurations
        self.retry_configs = {
            "PROCESSING_ERROR": {"max_retries": 3, "delay": 1},
            "RATE_LIMIT_ERROR": {"max_retries": 2, "delay": 5},
            "DEFAULT": {"max_retries": 1, "delay": 1}
        }

    def log_error(self, error: AgentError, context: Optional[Dict[str, Any]] = None):
        """Log error with context."""
        error.metadata.context.update(context or {})
        error.metadata.stack_trace = traceback.format_exc()
        
        log_entry = {
            "timestamp": error.metadata.timestamp.isoformat(),
            "error_code": error.error_code,
            "message": error.message,
            "metadata": error.metadata.model_dump()
        }
        
        logger.error(json.dumps(log_entry))

    def create_error_response(self, 
                            error: AgentError, 
                            user_message: bool = True) -> ErrorResponse:
        """Create standardized error response."""
        template = self.response_templates.get(
            error.error_code,
            self.response_templates["DEFAULT"]
        )
        
        return ErrorResponse(
            error_code=error.error_code,
            message=template if user_message else error.message,
            details=str(error) if not user_message else None,
            metadata=error.metadata
        )

    async def handle_with_retry(self,
                              func: callable,
                              *args,
                              error_context: Optional[Dict[str, Any]] = None,
                              **kwargs) -> Any:
        """Execute function with retry logic."""
        error_code = "DEFAULT"
        max_retries = self.retry_configs[error_code]["max_retries"]
        delay = self.retry_configs[error_code]["delay"]
        
        for attempt in range(max_retries + 1):
            try:
                return await func(*args, **kwargs)
            except AgentError as e:
                error_code = e.error_code
                config = self.retry_configs.get(
                    error_code,
                    self.retry_configs["DEFAULT"]
                )
                
                if attempt < config["max_retries"]:
                    # Update metadata and log retry attempt
                    e.metadata.retry_count = attempt + 1
                    self.log_error(e, error_context)
                    
                    # Wait before retrying
                    await asyncio.sleep(config["delay"])
                    continue
                
                # Max retries reached, raise final error
                raise
            except Exception as e:
                # Handle unexpected errors
                error = ProcessingError(
                    message=str(e),
                    metadata=ErrorMetadata(
                        severity="error",
                        category="unexpected",
                        context=error_context or {}
                    )
                )
                self.log_error(error)
                raise error

def with_error_handling(error_context: Optional[Dict[str, Any]] = None):
    """Decorator for error handling."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except AgentError as e:
                error_handler.log_error(e, error_context)
                return error_handler.create_error_response(e)
            except Exception as e:
                error = ProcessingError(
                    message=str(e),
                    metadata=ErrorMetadata(
                        severity="error",
                        category="unexpected",
                        context=error_context or {}
                    )
                )
                error_handler.log_error(error)
                return error_handler.create_error_response(error)
        return wrapper
    return decorator

# Create singleton instance
error_handler = ErrorHandler()