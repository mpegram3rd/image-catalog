"""Custom exception classes for image-catalog backend.

This module defines a hierarchy of custom exceptions that provide structured
error handling throughout the application. Each exception includes context
information and appropriate HTTP status codes for API responses.
"""

from typing import Any, Dict, Optional


class ImageCatalogError(Exception):
    """Base exception for all image-catalog errors.

    Provides a common interface for all application-specific exceptions
    with support for error codes, context, and HTTP status mapping.
    """

    def __init__(
        self,
        message: str,
        error_code: str = "GENERIC_ERROR",
        context: Optional[Dict[str, Any]] = None,
        http_status: int = 500,
        cause: Optional[Exception] = None,
    ):
        """Initialize the base exception.

        Args:
            message: Human-readable error message
            error_code: Machine-readable error code for API responses
            context: Additional context information for debugging
            http_status: HTTP status code for API responses
            cause: The underlying exception that caused this error
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.context = context or {}
        self.http_status = http_status
        self.cause = cause

    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for API responses."""
        result = {
            "error": {
                "code": self.error_code,
                "message": self.message,
                "type": self.__class__.__name__,
            }
        }

        if self.context:
            result["error"]["context"] = self.context

        if self.cause:
            result["error"]["cause"] = str(self.cause)

        return result


class ConfigurationError(ImageCatalogError):
    """Raised when configuration is invalid or missing."""

    def __init__(
        self,
        message: str,
        config_field: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None,
    ):
        """Initialize configuration error.

        Args:
            message: Error description
            config_field: Name of the problematic configuration field
            context: Additional context
            cause: Underlying exception
        """
        error_context = context or {}
        if config_field:
            error_context["config_field"] = config_field

        super().__init__(
            message=message,
            error_code="CONFIGURATION_ERROR",
            context=error_context,
            http_status=500,
            cause=cause,
        )


class ImageProcessingError(ImageCatalogError):
    """Raised when image processing operations fail."""

    def __init__(
        self,
        message: str,
        image_path: Optional[str] = None,
        operation: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None,
    ):
        """Initialize image processing error.

        Args:
            message: Error description
            image_path: Path to the image that failed processing
            operation: Name of the operation that failed
            context: Additional context
            cause: Underlying exception
        """
        error_context = context or {}
        if image_path:
            error_context["image_path"] = image_path
        if operation:
            error_context["operation"] = operation

        super().__init__(
            message=message,
            error_code="IMAGE_PROCESSING_ERROR",
            context=error_context,
            http_status=422,
            cause=cause,
        )


class SearchError(ImageCatalogError):
    """Raised when search operations fail."""

    def __init__(
        self,
        message: str,
        search_query: Optional[str] = None,
        search_type: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None,
    ):
        """Initialize search error.

        Args:
            message: Error description
            search_query: The search query that failed
            search_type: Type of search (text, image, multimodal)
            context: Additional context
            cause: Underlying exception
        """
        error_context = context or {}
        if search_query:
            error_context["search_query"] = search_query
        if search_type:
            error_context["search_type"] = search_type

        super().__init__(
            message=message,
            error_code="SEARCH_ERROR",
            context=error_context,
            http_status=422,
            cause=cause,
        )


class DatabaseError(ImageCatalogError):
    """Raised when database operations fail."""

    def __init__(
        self,
        message: str,
        operation: Optional[str] = None,
        collection: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None,
    ):
        """Initialize database error.

        Args:
            message: Error description
            operation: Database operation that failed
            collection: ChromaDB collection name
            context: Additional context
            cause: Underlying exception
        """
        error_context = context or {}
        if operation:
            error_context["operation"] = operation
        if collection:
            error_context["collection"] = collection

        super().__init__(
            message=message,
            error_code="DATABASE_ERROR",
            context=error_context,
            http_status=503,
            cause=cause,
        )


class AIServiceError(ImageCatalogError):
    """Raised when AI service calls fail."""

    def __init__(
        self,
        message: str,
        service: Optional[str] = None,
        model: Optional[str] = None,
        retry_count: int = 0,
        context: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None,
    ):
        """Initialize AI service error.

        Args:
            message: Error description
            service: AI service name (OpenAI, etc.)
            model: Model name that failed
            retry_count: Number of retries attempted
            context: Additional context
            cause: Underlying exception
        """
        error_context = context or {}
        if service:
            error_context["service"] = service
        if model:
            error_context["model"] = model
        if retry_count > 0:
            error_context["retry_count"] = retry_count

        super().__init__(
            message=message,
            error_code="AI_SERVICE_ERROR",
            context=error_context,
            http_status=502,
            cause=cause,
        )


class ValidationError(ImageCatalogError):
    """Raised when input validation fails."""

    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        value: Optional[Any] = None,
        context: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None,
    ):
        """Initialize validation error.

        Args:
            message: Error description
            field: Name of the field that failed validation
            value: The invalid value (if safe to include)
            context: Additional context
            cause: Underlying exception
        """
        error_context = context or {}
        if field:
            error_context["field"] = field
        if value is not None:
            # Only include value if it's safe (not sensitive data)
            if not isinstance(value, str) or len(str(value)) < 100:
                error_context["value"] = value

        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            context=error_context,
            http_status=400,
            cause=cause,
        )


class NotFoundError(ImageCatalogError):
    """Raised when a requested resource is not found."""

    def __init__(
        self,
        message: str,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ):
        """Initialize not found error.

        Args:
            message: Error description
            resource_type: Type of resource (image, collection, etc.)
            resource_id: ID or path of the missing resource
            context: Additional context
        """
        error_context = context or {}
        if resource_type:
            error_context["resource_type"] = resource_type
        if resource_id:
            error_context["resource_id"] = resource_id

        super().__init__(
            message=message,
            error_code="NOT_FOUND",
            context=error_context,
            http_status=404,
        )


class RateLimitError(ImageCatalogError):
    """Raised when rate limits are exceeded."""

    def __init__(
        self,
        message: str,
        limit_type: Optional[str] = None,
        retry_after: Optional[int] = None,
        context: Optional[Dict[str, Any]] = None,
    ):
        """Initialize rate limit error.

        Args:
            message: Error description
            limit_type: Type of rate limit (API, search, etc.)
            retry_after: Seconds until retry is allowed
            context: Additional context
        """
        error_context = context or {}
        if limit_type:
            error_context["limit_type"] = limit_type
        if retry_after:
            error_context["retry_after"] = retry_after

        super().__init__(
            message=message,
            error_code="RATE_LIMIT_EXCEEDED",
            context=error_context,
            http_status=429,
        )


class ServiceUnavailableError(ImageCatalogError):
    """Raised when a required service is unavailable."""

    def __init__(
        self,
        message: str,
        service: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None,
    ):
        """Initialize service unavailable error.

        Args:
            message: Error description
            service: Name of the unavailable service
            context: Additional context
            cause: Underlying exception
        """
        error_context = context or {}
        if service:
            error_context["service"] = service

        super().__init__(
            message=message,
            error_code="SERVICE_UNAVAILABLE",
            context=error_context,
            http_status=503,
            cause=cause,
        )