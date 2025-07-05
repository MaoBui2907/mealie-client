"""
Integration tests for error handling scenarios.

Tests cover HTTP errors, network issues, timeout handling,
retry mechanisms, and exception propagation.
"""

import pytest
import httpx
import respx

from mealie_client import MealieClient
from mealie_client.exceptions import (
    AuthenticationError,
    AuthorizationError,
    ConnectionError,
    TimeoutError,
    RateLimitError,
    ValidationError,
    NotFoundError,
    MealieAPIError,
)


class TestHTTPErrorHandling:
    """Test suite for HTTP error status code handling."""

    @pytest.mark.integration
    async def test_400_bad_request_error(self, integration_httpx_mock, authenticated_client):
        """Test handling of 400 Bad Request errors."""
        integration_httpx_mock.post("/api/recipes").mock(
            return_value=httpx.Response(400, json={
                "detail": "Invalid recipe data",
                "validation_errors": ["Name is required"]
            })
        )
        
        with pytest.raises(ValidationError) as exc_info:
            await authenticated_client.post("recipes", json={"invalid": "data"})
        
        assert exc_info.value.status_code == 400
        assert "Invalid recipe data" in str(exc_info.value)

    @pytest.mark.integration
    async def test_401_unauthorized_error(self, integration_httpx_mock, authenticated_client):
        """Test handling of 401 Unauthorized errors."""
        integration_httpx_mock.get("/api/recipes").mock(
            return_value=httpx.Response(401, json={"detail": "Token expired"})
        )
        
        with pytest.raises(AuthenticationError) as exc_info:
            await authenticated_client.get("recipes")
        
        assert exc_info.value.status_code == 401
        assert "Token expired" in str(exc_info.value)

    @pytest.mark.integration
    async def test_403_forbidden_error(self, integration_httpx_mock, authenticated_client):
        """Test handling of 403 Forbidden errors."""
        integration_httpx_mock.delete("/api/recipes/admin-recipe").mock(
            return_value=httpx.Response(403, json={"detail": "Insufficient permissions"})
        )
        
        with pytest.raises(AuthorizationError) as exc_info:
            await authenticated_client.delete("recipes/admin-recipe")
        
        assert exc_info.value.status_code == 403
        assert "Insufficient permissions" in str(exc_info.value)

    @pytest.mark.integration
    async def test_404_not_found_error(self, integration_httpx_mock, authenticated_client):
        """Test handling of 404 Not Found errors."""
        integration_httpx_mock.get("/api/recipes/nonexistent").mock(
            return_value=httpx.Response(404, json={"detail": "Recipe not found"})
        )
        
        with pytest.raises(NotFoundError) as exc_info:
            await authenticated_client.get("recipes/nonexistent")
        
        assert exc_info.value.status_code == 404
        assert "Recipe not found" in str(exc_info.value)

    @pytest.mark.integration
    async def test_429_rate_limit_error(self, integration_httpx_mock, authenticated_client):
        """Test handling of 429 Too Many Requests errors."""
        integration_httpx_mock.get("/api/recipes").mock(
            return_value=httpx.Response(429, json={
                "detail": "Rate limit exceeded",
                "retry_after": 60
            }, headers={"Retry-After": "60"})
        )
        
        with pytest.raises(RateLimitError) as exc_info:
            await authenticated_client.get("recipes")
        
        assert exc_info.value.status_code == 429
        assert exc_info.value.retry_after == 60
        assert "Rate limit exceeded" in str(exc_info.value)

    @pytest.mark.integration
    async def test_500_server_error(self, integration_httpx_mock, authenticated_client):
        """Test handling of 500 Internal Server Error."""
        integration_httpx_mock.get("/api/recipes").mock(
            return_value=httpx.Response(500, json={"detail": "Internal server error"})
        )
        
        with pytest.raises(MealieAPIError) as exc_info:
            await authenticated_client.get("recipes")
        
        assert exc_info.value.status_code == 500
        assert "Internal server error" in str(exc_info.value)


class TestNetworkErrorHandling:
    """Test suite for network-level error handling."""

    @pytest.mark.integration
    async def test_connection_timeout_error(self, integration_httpx_mock, authenticated_client):
        """Test handling of connection timeout errors."""
        integration_httpx_mock.get("/api/recipes").mock(
            side_effect=httpx.TimeoutException("Request timed out")
        )
        
        with pytest.raises(TimeoutError) as exc_info:
            await authenticated_client.get("recipes")
        
        assert "Request timed out" in str(exc_info.value)

    @pytest.mark.integration
    async def test_connection_error(self, integration_httpx_mock, authenticated_client):
        """Test handling of connection errors."""
        integration_httpx_mock.get("/api/recipes").mock(
            side_effect=httpx.ConnectError("Connection failed")
        )
        
        with pytest.raises(ConnectionError) as exc_info:
            await authenticated_client.get("recipes")
        
        assert "Connection failed" in str(exc_info.value)


class TestRetryMechanism:
    """Test suite for automatic retry mechanisms."""

    @pytest.mark.integration
    async def test_retry_on_connection_error(self, base_url, test_credentials):
        """Test automatic retry on connection errors."""
        retry_count = 0
        
        def side_effect(*args, **kwargs):
            nonlocal retry_count
            retry_count += 1
            if retry_count <= 2:  # Fail first 2 attempts
                raise httpx.ConnectError("Connection failed")
            else:  # Succeed on 3rd attempt
                return httpx.Response(200, json={"success": True})
        
        with respx.mock() as mock:
            mock.post("/api/auth/token").mock(
                return_value=httpx.Response(200, json={
                    "access_token": "retry_test_token",
                    "refresh_token": "retry_test_refresh",
                    "token_type": "bearer",
                    "expires_in": 3600
                })
            )
            mock.get("/api/recipes").mock(side_effect=side_effect)
            
            client = MealieClient(
                base_url=base_url,
                username=test_credentials["username"],
                password=test_credentials["password"],
                max_retries=3
            )
            
            await client.start_session()
            
            # Should succeed after retries
            response = await client.get("recipes")
            assert response["success"] is True
            assert retry_count == 3  # Failed twice, succeeded on third
            
            await client.close_session()

    @pytest.mark.integration
    async def test_no_retry_on_client_errors(self, integration_httpx_mock, authenticated_client):
        """Test that client errors (4xx) don't trigger retries."""
        call_count = 0
        
        def side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            return httpx.Response(400, json={"detail": "Bad request"})
        
        integration_httpx_mock.get("/api/recipes").mock(side_effect=side_effect)
        
        with pytest.raises(ValidationError):
            await authenticated_client.get("recipes")
        
        # Should only be called once (no retries for 4xx)
        assert call_count == 1
