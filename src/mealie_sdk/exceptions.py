"""
Custom exceptions for the Mealie SDK.

This module defines all custom exceptions that can be raised by the SDK,
providing clear error messages and proper exception hierarchy.
"""

from typing import Any, Dict, Optional


class MealieSDKError(Exception):
    """Base exception class for all Mealie SDK errors."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        """
        Initialize the exception.

        Args:
            message: Human-readable error message
            details: Optional dictionary with additional error details
        """
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def __str__(self) -> str:
        """Return string representation of the exception."""
        if self.details:
            return f"{self.message} (Details: {self.details})"
        return self.message


class MealieAPIError(MealieSDKError):
    """Raised when the Mealie API returns an error response."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_data: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None,
    ) -> None:
        """
        Initialize the API error.

        Args:
            message: Error message from the API or SDK
            status_code: HTTP status code from the response
            response_data: Raw response data from the API
            request_id: Request ID for debugging purposes
        """
        details = {}
        if status_code is not None:
            details["status_code"] = status_code
        if response_data is not None:
            details["response_data"] = response_data
        if request_id is not None:
            details["request_id"] = request_id

        super().__init__(message, details)
        self.status_code = status_code
        self.response_data = response_data
        self.request_id = request_id


class AuthenticationError(MealieAPIError):
    """Raised when authentication fails."""

    def __init__(
        self,
        message: str = "Authentication failed",
        status_code: Optional[int] = 401,
        response_data: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Initialize the authentication error.

        Args:
            message: Error message
            status_code: HTTP status code (defaults to 401)
            response_data: Raw response data from the API
        """
        super().__init__(message, status_code, response_data)


class AuthorizationError(MealieAPIError):
    """Raised when the user doesn't have permission to access a resource."""

    def __init__(
        self,
        message: str = "Insufficient permissions to access this resource",
        status_code: Optional[int] = 403,
        response_data: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Initialize the authorization error.

        Args:
            message: Error message
            status_code: HTTP status code (defaults to 403)
            response_data: Raw response data from the API
        """
        super().__init__(message, status_code, response_data)


class NotFoundError(MealieAPIError):
    """Raised when a requested resource is not found."""

    def __init__(
        self,
        message: str = "The requested resource was not found",
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        status_code: Optional[int] = 404,
        response_data: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Initialize the not found error.

        Args:
            message: Error message
            resource_type: Type of resource that was not found (e.g., "recipe")
            resource_id: ID or slug of the resource that was not found
            status_code: HTTP status code (defaults to 404)
            response_data: Raw response data from the API
        """
        if resource_type and resource_id:
            message = f"{resource_type.title()} '{resource_id}' not found"

        details = {}
        if resource_type:
            details["resource_type"] = resource_type
        if resource_id:
            details["resource_id"] = resource_id

        super().__init__(message, status_code, response_data)
        self.details.update(details)


class ValidationError(MealieAPIError):
    """Raised when request data fails validation."""

    def __init__(
        self,
        message: str = "Request data validation failed",
        validation_errors: Optional[Dict[str, Any]] = None,
        status_code: Optional[int] = 422,
        response_data: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Initialize the validation error.

        Args:
            message: Error message
            validation_errors: Dictionary of field validation errors
            status_code: HTTP status code (defaults to 422)
            response_data: Raw response data from the API
        """
        if validation_errors:
            details = {"validation_errors": validation_errors}
        else:
            details = {}

        super().__init__(message, status_code, response_data)
        self.details.update(details)
        self.validation_errors = validation_errors


class RateLimitError(MealieAPIError):
    """Raised when API rate limit is exceeded."""

    def __init__(
        self,
        message: str = "API rate limit exceeded",
        retry_after: Optional[int] = None,
        status_code: Optional[int] = 429,
        response_data: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Initialize the rate limit error.

        Args:
            message: Error message
            retry_after: Number of seconds to wait before retrying
            status_code: HTTP status code (defaults to 429)
            response_data: Raw response data from the API
        """
        details = {}
        if retry_after is not None:
            details["retry_after"] = retry_after

        super().__init__(message, status_code, response_data)
        self.details.update(details)
        self.retry_after = retry_after


class ConnectionError(MealieSDKError):
    """Raised when there's a connection problem with the Mealie server."""

    def __init__(
        self,
        message: str = "Failed to connect to Mealie server",
        original_error: Optional[Exception] = None,
    ) -> None:
        """
        Initialize the connection error.

        Args:
            message: Error message
            original_error: The original exception that caused this error
        """
        details = {}
        if original_error:
            details["original_error"] = str(original_error)
            details["error_type"] = type(original_error).__name__

        super().__init__(message, details)
        self.original_error = original_error


class TimeoutError(MealieSDKError):
    """Raised when a request times out."""

    def __init__(
        self,
        message: str = "Request timed out",
        timeout_duration: Optional[float] = None,
    ) -> None:
        """
        Initialize the timeout error.

        Args:
            message: Error message
            timeout_duration: The timeout duration in seconds
        """
        details = {}
        if timeout_duration is not None:
            details["timeout_duration"] = timeout_duration

        super().__init__(message, details)
        self.timeout_duration = timeout_duration


class ConfigurationError(MealieSDKError):
    """Raised when there's a configuration problem with the SDK."""

    def __init__(
        self,
        message: str,
        config_field: Optional[str] = None,
        expected_type: Optional[str] = None,
        actual_value: Optional[Any] = None,
    ) -> None:
        """
        Initialize the configuration error.

        Args:
            message: Error message
            config_field: The configuration field that has an issue
            expected_type: The expected type for the configuration field
            actual_value: The actual value that was provided
        """
        details = {}
        if config_field:
            details["config_field"] = config_field
        if expected_type:
            details["expected_type"] = expected_type
        if actual_value is not None:
            details["actual_value"] = actual_value

        super().__init__(message, details)


class FileOperationError(MealieSDKError):
    """Raised when file operations fail."""

    def __init__(
        self,
        message: str,
        file_path: Optional[str] = None,
        operation: Optional[str] = None,
        original_error: Optional[Exception] = None,
    ) -> None:
        """
        Initialize the file operation error.

        Args:
            message: Error message
            file_path: Path to the file that caused the error
            operation: The operation that failed (e.g., "upload", "download")
            original_error: The original exception that caused this error
        """
        details = {}
        if file_path:
            details["file_path"] = file_path
        if operation:
            details["operation"] = operation
        if original_error:
            details["original_error"] = str(original_error)

        super().__init__(message, details)
        self.original_error = original_error


def create_api_error_from_response(
    status_code: int,
    response_data: Optional[Dict[str, Any]] = None,
    request_id: Optional[str] = None,
) -> MealieAPIError:
    """
    Create an appropriate API error based on the HTTP status code.

    Args:
        status_code: HTTP status code
        response_data: Response data from the API
        request_id: Request ID for debugging

    Returns:
        Appropriate exception instance based on the status code
    """
    # Extract error message from response data if available
    message = "API request failed"
    if response_data:
        if "detail" in response_data:
            message = response_data["detail"]
        elif "message" in response_data:
            message = response_data["message"]
        elif "error" in response_data:
            message = response_data["error"]

    # Create specific exception based on status code
    if status_code == 401:
        return AuthenticationError(message, status_code, response_data)
    elif status_code == 403:
        return AuthorizationError(message, status_code, response_data)
    elif status_code == 404:
        return NotFoundError(message, status_code=status_code, response_data=response_data)
    elif status_code == 422:
        validation_errors = None
        if response_data and "detail" in response_data:
            # Handle FastAPI validation error format
            if isinstance(response_data["detail"], list):
                validation_errors = {}
                for error in response_data["detail"]:
                    if "loc" in error and "msg" in error:
                        field_path = ".".join(str(loc) for loc in error["loc"])
                        validation_errors[field_path] = error["msg"]
        return ValidationError(message, validation_errors, status_code, response_data)
    elif status_code == 429:
        retry_after = None
        if response_data and "retry_after" in response_data:
            retry_after = response_data["retry_after"]
        return RateLimitError(message, retry_after, status_code, response_data)
    else:
        return MealieAPIError(message, status_code, response_data, request_id) 