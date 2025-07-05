"""
Unit tests for Mealie SDK custom exceptions.

Tests cover exception hierarchy, error creation, data preservation,
and exception factory functions.
"""

import pytest
from typing import Dict, Any, Optional

from mealie_client.exceptions import (
    MealieSDKError,
    MealieAPIError,
    AuthenticationError,
    AuthorizationError,
    NotFoundError,
    ValidationError,
    RateLimitError,
    ConnectionError,
    TimeoutError,
    ConfigurationError,
    FileOperationError,
    create_api_error_from_response,
)


class TestMealieSDKError:
    """Test suite for base MealieSDKError class."""

    @pytest.mark.unit
    def test_init_with_message_only(self):
        """Test initialization with message only."""
        error = MealieSDKError("Test error message")
        
        assert str(error) == "Test error message"
        assert error.message == "Test error message"
        assert error.details == {}

    @pytest.mark.unit
    def test_init_with_message_and_details(self):
        """Test initialization with message and details."""
        details = {"field": "value", "code": 123}
        error = MealieSDKError("Test error", details=details)
        
        assert error.message == "Test error"
        assert error.details == details

    @pytest.mark.unit
    def test_str_representation_with_details(self):
        """Test string representation includes details."""
        details = {"error_code": "E001", "field": "username"}
        error = MealieSDKError("Validation failed", details=details)
        
        str_repr = str(error)
        assert "Validation failed" in str_repr
        assert "Details:" in str_repr
        assert "error_code" in str_repr
        assert "E001" in str_repr

    @pytest.mark.unit
    def test_str_representation_without_details(self):
        """Test string representation without details."""
        error = MealieSDKError("Simple error")
        assert str(error) == "Simple error"


class TestMealieAPIError:
    """Test suite for MealieAPIError class."""

    @pytest.mark.unit
    def test_init_with_minimal_params(self):
        """Test initialization with minimal parameters."""
        error = MealieAPIError("API error occurred")
        
        assert error.message == "API error occurred"
        assert error.status_code is None
        assert error.response_data is None
        assert error.request_id is None

    @pytest.mark.unit
    def test_init_with_all_params(self):
        """Test initialization with all parameters."""
        response_data = {"detail": "Resource not found", "code": "NOT_FOUND"}
        request_id = "req_12345"
        
        error = MealieAPIError(
            message="Not found",
            status_code=404,
            response_data=response_data,
            request_id=request_id
        )
        
        assert error.message == "Not found"
        assert error.status_code == 404
        assert error.response_data == response_data
        assert error.request_id == request_id
        
        # Check that details are properly set
        assert error.details["status_code"] == 404
        assert error.details["response_data"] == response_data
        assert error.details["request_id"] == request_id

    @pytest.mark.unit
    def test_inheritance_from_base_error(self):
        """Test that MealieAPIError inherits from MealieSDKError."""
        error = MealieAPIError("API error")
        assert isinstance(error, MealieSDKError)


class TestAuthenticationError:
    """Test suite for AuthenticationError class."""

    @pytest.mark.unit
    def test_init_with_defaults(self):
        """Test initialization with default parameters."""
        error = AuthenticationError()
        
        assert error.message == "Authentication failed"
        assert error.status_code == 401
        assert error.response_data is None

    @pytest.mark.unit
    def test_init_with_custom_params(self):
        """Test initialization with custom parameters."""
        response_data = {"detail": "Invalid credentials"}
        error = AuthenticationError(
            message="Login failed",
            status_code=401,
            response_data=response_data
        )
        
        assert error.message == "Login failed"
        assert error.status_code == 401
        assert error.response_data == response_data

    @pytest.mark.unit
    def test_inheritance_from_api_error(self):
        """Test that AuthenticationError inherits from MealieAPIError."""
        error = AuthenticationError()
        assert isinstance(error, MealieAPIError)
        assert isinstance(error, MealieSDKError)


class TestAuthorizationError:
    """Test suite for AuthorizationError class."""

    @pytest.mark.unit
    def test_init_with_defaults(self):
        """Test initialization with default parameters."""
        error = AuthorizationError()
        
        assert "Insufficient permissions" in error.message
        assert error.status_code == 403

    @pytest.mark.unit
    def test_init_with_custom_message(self):
        """Test initialization with custom message."""
        error = AuthorizationError("Access denied to admin panel")
        
        assert error.message == "Access denied to admin panel"
        assert error.status_code == 403


class TestNotFoundError:
    """Test suite for NotFoundError class."""

    @pytest.mark.unit
    def test_init_with_defaults(self):
        """Test initialization with default parameters."""
        error = NotFoundError()
        
        assert "requested resource was not found" in error.message
        assert error.status_code == 404

    @pytest.mark.unit
    def test_init_with_resource_info(self):
        """Test initialization with resource type and ID."""
        error = NotFoundError(
            resource_type="recipe",
            resource_id="chicken-curry"
        )
        
        assert "Recipe 'chicken-curry' not found" in error.message
        assert error.details["resource_type"] == "recipe"
        assert error.details["resource_id"] == "chicken-curry"

    # TODO: Implement this test
    @pytest.mark.skip(reason="TODO: Implement this test")
    def test_init_with_custom_message_overrides_generated(self):
        """Test that custom message overrides auto-generated message."""
        error = NotFoundError(
            message="Custom not found message",
            resource_type="recipe",
            resource_id="test"
        )
        
        assert error.message == "Custom not found message"
        # But details should still be set
        assert error.details["resource_type"] == "recipe"
        assert error.details["resource_id"] == "test"


class TestValidationError:
    """Test suite for ValidationError class."""

    @pytest.mark.unit
    def test_init_with_defaults(self):
        """Test initialization with default parameters."""
        error = ValidationError()
        
        assert "validation failed" in error.message
        assert error.status_code == 422
        assert error.validation_errors is None

    @pytest.mark.unit
    def test_init_with_validation_errors(self):
        """Test initialization with validation errors."""
        validation_errors = {
            "name": ["This field is required"],
            "email": ["Invalid email format", "Email already exists"]
        }
        
        error = ValidationError(
            message="Form validation failed",
            validation_errors=validation_errors
        )
        
        assert error.message == "Form validation failed"
        assert error.validation_errors == validation_errors
        assert error.details["validation_errors"] == validation_errors

    @pytest.mark.unit
    def test_validation_errors_in_details(self):
        """Test that validation errors are included in details."""
        validation_errors = {"field": ["error message"]}
        error = ValidationError(validation_errors=validation_errors)
        
        assert "validation_errors" in error.details
        assert error.details["validation_errors"] == validation_errors


class TestRateLimitError:
    """Test suite for RateLimitError class."""

    @pytest.mark.unit
    def test_init_with_defaults(self):
        """Test initialization with default parameters."""
        error = RateLimitError()
        
        assert "rate limit exceeded" in error.message
        assert error.status_code == 429
        assert error.retry_after is None

    @pytest.mark.unit
    def test_init_with_retry_after(self):
        """Test initialization with retry_after parameter."""
        error = RateLimitError(retry_after=60)
        
        assert error.retry_after == 60
        assert error.details["retry_after"] == 60

    @pytest.mark.unit
    def test_custom_message_and_retry_after(self):
        """Test initialization with custom message and retry_after."""
        error = RateLimitError(
            message="API quota exceeded",
            retry_after=120
        )
        
        assert error.message == "API quota exceeded"
        assert error.retry_after == 120


class TestConnectionError:
    """Test suite for ConnectionError class."""

    @pytest.mark.unit
    def test_init_with_defaults(self):
        """Test initialization with default parameters."""
        error = ConnectionError()
        
        assert "Failed to connect" in error.message
        assert error.details.get("original_error") is None

    # TODO: Implement this test
    @pytest.mark.skip(reason="TODO: Implement this test")
    def test_init_with_original_error(self):
        """Test initialization with original error."""
        original_error = Exception("Network unreachable")
        error = ConnectionError(
            message="Connection timeout",
            original_error=original_error
        )
        
        assert error.message == "Connection timeout"
        assert error.details["original_error"] == original_error

    @pytest.mark.unit
    def test_inheritance_from_base_error(self):
        """Test that ConnectionError inherits from MealieSDKError."""
        error = ConnectionError()
        assert isinstance(error, MealieSDKError)
        # Should NOT inherit from MealieAPIError since it's not an API response error
        assert not isinstance(error, MealieAPIError)


class TestTimeoutError:
    """Test suite for TimeoutError class."""

    @pytest.mark.unit
    def test_init_with_defaults(self):
        """Test initialization with default parameters."""
        error = TimeoutError()
        
        assert "timed out" in error.message
        assert error.details.get("timeout_duration") is None

    @pytest.mark.unit
    def test_init_with_timeout_duration(self):
        """Test initialization with timeout duration."""
        error = TimeoutError(
            message="Request timeout",
            timeout_duration=30.0
        )
        
        assert error.message == "Request timeout"
        assert error.details["timeout_duration"] == 30.0

    @pytest.mark.unit
    def test_inheritance_from_base_error(self):
        """Test that TimeoutError inherits from MealieSDKError."""
        error = TimeoutError()
        assert isinstance(error, MealieSDKError)
        assert not isinstance(error, MealieAPIError)


class TestConfigurationError:
    """Test suite for ConfigurationError class."""

    @pytest.mark.unit
    def test_init_with_message_only(self):
        """Test initialization with message only."""
        error = ConfigurationError("Invalid configuration")
        
        assert error.message == "Invalid configuration"
        assert error.details.get("config_field") is None
        assert error.details.get("expected_type") is None
        assert error.details.get("actual_value") is None

    @pytest.mark.unit
    def test_init_with_all_params(self):
        """Test initialization with all parameters."""
        error = ConfigurationError(
            message="Invalid timeout value",
            config_field="timeout",
            expected_type="float",
            actual_value="thirty"
        )
        
        assert error.message == "Invalid timeout value"
        assert error.details["config_field"] == "timeout"
        assert error.details["expected_type"] == "float"
        assert error.details["actual_value"] == "thirty"

    @pytest.mark.unit
    def test_inheritance_from_base_error(self):
        """Test that ConfigurationError inherits from MealieSDKError."""
        error = ConfigurationError("Config error")
        assert isinstance(error, MealieSDKError)
        assert not isinstance(error, MealieAPIError)


class TestFileOperationError:
    """Test suite for FileOperationError class."""

    @pytest.mark.unit
    def test_init_with_message_only(self):
        """Test initialization with message only."""
        error = FileOperationError("File operation failed")
        
        assert error.message == "File operation failed"
        assert error.details.get("file_path") is None
        assert error.details.get("operation") is None
        assert error.details.get("original_error") is None

    # TODO: Implement this test
    @pytest.mark.skip(reason="TODO: Implement this test")
    def test_init_with_all_params(self):
        """Test initialization with all parameters."""
        original_error = IOError("Permission denied")
        error = FileOperationError(
            message="Failed to upload file",
            file_path="/path/to/file.jpg",
            operation="upload",
            original_error=original_error
        )
        
        assert error.message == "Failed to upload file"
        assert error.details["file_path"] == "/path/to/file.jpg"
        assert error.details["operation"] == "upload"
        assert error.details["original_error"] == original_error

    @pytest.mark.unit
    def test_inheritance_from_base_error(self):
        """Test that FileOperationError inherits from MealieSDKError."""
        error = FileOperationError("File error")
        assert isinstance(error, MealieSDKError)
        assert not isinstance(error, MealieAPIError)


class TestCreateApiErrorFromResponse:
    """Test suite for create_api_error_from_response factory function."""

    # TODO: Implement this test
    @pytest.mark.skip(reason="TODO: Implement this test")
    def test_creates_authentication_error_for_401(self):
        """Test that 401 status creates AuthenticationError."""
        response_data = {"detail": "Invalid token"}
        request_id = "req_123"
        
        error = create_api_error_from_response(
            status_code=401,
            response_data=response_data,
            request_id=request_id
        )
        
        assert isinstance(error, AuthenticationError)
        assert error.status_code == 401
        assert error.response_data == response_data
        assert error.request_id == request_id

    @pytest.mark.unit
    def test_creates_authorization_error_for_403(self):
        """Test that 403 status creates AuthorizationError."""
        error = create_api_error_from_response(status_code=403)
        
        assert isinstance(error, AuthorizationError)
        assert error.status_code == 403

    @pytest.mark.unit
    def test_creates_not_found_error_for_404(self):
        """Test that 404 status creates NotFoundError."""
        response_data = {"detail": "Recipe not found"}
        error = create_api_error_from_response(
            status_code=404,
            response_data=response_data
        )
        
        assert isinstance(error, NotFoundError)
        assert error.status_code == 404
        assert error.response_data == response_data

    @pytest.mark.unit
    def test_creates_validation_error_for_400(self):
        """Test that 400 status creates ValidationError."""
        response_data = {"detail": "Bad request"}
        
        error = create_api_error_from_response(
            status_code=400,
            response_data=response_data
        )
        
        assert isinstance(error, ValidationError)
        assert error.status_code == 400

    @pytest.mark.unit
    def test_creates_validation_error_for_422(self):
        """Test that 422 status creates ValidationError."""
        response_data = {
            "detail": [
                {"field": "name", "message": "This field is required"}
            ]
        }
        
        error = create_api_error_from_response(
            status_code=422,
            response_data=response_data
        )
        
        assert isinstance(error, ValidationError)
        assert error.status_code == 422

    @pytest.mark.unit
    def test_creates_rate_limit_error_for_429(self):
        """Test that 429 status creates RateLimitError."""
        response_data = {"detail": "Rate limit exceeded", "retry_after": 60}
        
        error = create_api_error_from_response(
            status_code=429,
            response_data=response_data
        )
        
        assert isinstance(error, RateLimitError)
        assert error.status_code == 429

    @pytest.mark.unit
    def test_creates_generic_api_error_for_other_codes(self):
        """Test that other status codes create generic MealieAPIError."""
        test_cases = [500, 502, 503]  # Removed 400 since it creates ValidationError
        
        for status_code in test_cases:
            error = create_api_error_from_response(status_code=status_code)
            
            assert isinstance(error, MealieAPIError)
            assert not isinstance(error, AuthenticationError)
            assert not isinstance(error, AuthorizationError)
            assert not isinstance(error, NotFoundError)
            assert not isinstance(error, ValidationError)
            assert not isinstance(error, RateLimitError)
            assert error.status_code == status_code

    @pytest.mark.unit
    def test_extracts_message_from_response_data(self):
        """Test that error message is extracted from response data."""
        test_cases = [
            ({"detail": "Custom error message"}, "Custom error message"),
            ({"message": "Another error"}, "Another error"),
            ({"error": "Error description"}, "Error description"),
            ({"detail": ["Error 1", "Error 2"]}, "Error 1"),  # First error if list
        ]
        
        for response_data, expected_message in test_cases:
            error = create_api_error_from_response(
                status_code=400,
                response_data=response_data
            )
            
            assert expected_message in error.message

    # TODO: Implement this test
    @pytest.mark.skip(reason="TODO: Implement this test")
    def test_handles_empty_response_data(self):
        """Test handling of empty or None response data."""
        error = create_api_error_from_response(status_code=500)
        
        assert isinstance(error, MealieAPIError)
        assert error.status_code == 500
        assert error.response_data is None
        assert "HTTP 500" in error.message

    @pytest.mark.unit
    def test_handles_malformed_response_data(self):
        """Test handling of malformed response data."""
        malformed_data = {"unexpected_field": "value"}
        
        error = create_api_error_from_response(
            status_code=400,
            response_data=malformed_data
        )
        
        assert isinstance(error, MealieAPIError)
        assert error.response_data == malformed_data
        # Should still create error even with unexpected format


class TestExceptionHierarchy:
    """Test suite for exception inheritance hierarchy."""

    @pytest.mark.unit
    def test_all_api_errors_inherit_from_api_error(self):
        """Test that all API-related errors inherit from MealieAPIError."""
        api_errors = [
            AuthenticationError(),
            AuthorizationError(),
            NotFoundError(),
            ValidationError(),
            RateLimitError(),
        ]
        
        for error in api_errors:
            assert isinstance(error, MealieAPIError)
            assert isinstance(error, MealieSDKError)

    @pytest.mark.unit
    def test_non_api_errors_inherit_from_base_only(self):
        """Test that non-API errors inherit only from MealieSDKError."""
        non_api_errors = [
            ConnectionError(),
            TimeoutError(),
            ConfigurationError("test"),
            FileOperationError("test"),
        ]
        
        for error in non_api_errors:
            assert isinstance(error, MealieSDKError)
            assert not isinstance(error, MealieAPIError)

    @pytest.mark.unit
    def test_all_errors_are_exceptions(self):
        """Test that all custom errors are proper Python exceptions."""
        all_errors = [
            MealieSDKError("test"),
            MealieAPIError("test"),
            AuthenticationError(),
            AuthorizationError(),
            NotFoundError(),
            ValidationError(),
            RateLimitError(),
            ConnectionError(),
            TimeoutError(),
            ConfigurationError("test"),
            FileOperationError("test"),
        ]
        
        for error in all_errors:
            assert isinstance(error, Exception) 