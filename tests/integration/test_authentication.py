"""
Integration tests for authentication system.

Tests cover login/logout flows, token management, auto-refresh mechanisms,
and authentication error scenarios.
"""

import asyncio
from datetime import UTC, datetime, timedelta

import pytest
import httpx

from mealie_client import MealieClient, MealieAuth
from mealie_client.exceptions import (
    AuthenticationError,
    ConfigurationError,
    ConnectionError,
)


class TestBasicAuthentication:
    """Test suite for basic authentication flows."""

    @pytest.mark.integration
    async def test_username_password_login_success(self, integration_httpx_mock, base_url, test_credentials):
        """Test successful login with username/password."""
        # Mock successful login response
        integration_httpx_mock.post("/api/auth/token").mock(
            return_value=httpx.Response(200, json={
                "access_token": "success_access_token",
                "refresh_token": "success_refresh_token",
                "token_type": "bearer", 
                "expires_in": 3600
            })
        )
        
        client = MealieClient(
            base_url=base_url,
            username=test_credentials["username"],
            password=test_credentials["password"]
        )
        
        await client.start_session()
        
        # Verify authentication state
        assert client.auth.is_authenticated is True
        assert client.auth._access_token == "success_access_token"
        assert client.auth._refresh_token == "success_refresh_token"
        
        await client.close_session()

    @pytest.mark.integration
    async def test_username_password_login_failure(self, integration_httpx_mock, base_url):
        """Test login failure with invalid credentials."""
        # Mock failed login response
        integration_httpx_mock.post("/api/auth/token").mock(
            return_value=httpx.Response(401, json={"detail": "Invalid credentials"})
        )
        
        client = MealieClient(
            base_url=base_url,
            username="invalid_user",
            password="invalid_password"
        )
        
        with pytest.raises(AuthenticationError) as exc_info:
            await client.start_session()
        
        assert exc_info.value.status_code == 401
        assert "Invalid" in str(exc_info.value)

    @pytest.mark.integration
    async def test_api_token_authentication(self, integration_httpx_mock, base_url, test_credentials):
        """Test API token authentication (no login required)."""
        # Mock some API endpoint to verify token is used
        integration_httpx_mock.get("/api/recipes").mock(
            return_value=httpx.Response(200, json={"items": []})
        )
        
        client = MealieClient(
            base_url=base_url,
            api_token=test_credentials["api_token"]
        )
        
        await client.start_session()
        
        # Verify token auth state
        assert client.auth.is_token_auth is True
        assert client.auth.is_authenticated is True
        assert client.auth.api_token == test_credentials["api_token"]
        
        # Verify API calls use the token
        await client.get("recipes")
        
        request = integration_httpx_mock.calls[-1].request
        assert "Authorization" in request.headers
        assert request.headers["Authorization"] == f"Bearer {test_credentials['api_token']}"
        
        await client.close_session()

    @pytest.mark.integration
    async def test_missing_credentials_error(self, base_url):
        """Test error when no authentication credentials provided."""
        with pytest.raises(ConfigurationError) as exc_info:
            MealieClient(base_url=base_url)
        
        assert "authentication" in str(exc_info.value).lower()

    @pytest.mark.integration
    async def test_manual_login_call(self, integration_httpx_mock, base_url, test_credentials):
        """Test manual login() method call."""
        integration_httpx_mock.post("/api/auth/token").mock(
            return_value=httpx.Response(200, json={
                "access_token": "manual_login_token",
                "refresh_token": "manual_refresh_token",
                "token_type": "bearer",
                "expires_in": 3600
            })
        )
        
        client = MealieClient(
            base_url=base_url,
            username=test_credentials["username"],
            password=test_credentials["password"]
        )
        
        await client.start_session()
        
        # Manual login should update tokens
        await client.login()
        
        assert client.auth._access_token == "manual_login_token"
        assert client.auth._refresh_token == "manual_refresh_token"
        
        await client.close_session()


class TestTokenManagement:
    """Test suite for token lifecycle management."""

    @pytest.mark.integration
    async def test_token_storage_and_retrieval(self, integration_httpx_mock, base_url, test_credentials):
        """Test that tokens are properly stored and retrieved."""
        integration_httpx_mock.post("/api/auth/token").mock(
            return_value=httpx.Response(200, json={
                "access_token": "stored_token",
                "refresh_token": "stored_refresh", 
                "token_type": "bearer",
                "expires_in": 3600
            })
        )
        
        client = MealieClient(
            base_url=base_url,
            username=test_credentials["username"],
            password=test_credentials["password"]
        )
        
        await client.start_session()
        
        # Verify token storage
        assert client.auth._access_token == "stored_token"
        assert client.auth._refresh_token == "stored_refresh"
        assert client.auth._token_expires_at is not None
        
        # Verify auth headers
        headers = await client.auth.get_auth_headers()
        assert headers["Authorization"] == "Bearer stored_token"
        
        await client.close_session()

    @pytest.mark.integration
    async def test_token_expiry_detection(self, integration_httpx_mock, base_url, test_credentials):
        """Test detection of token expiry."""
        client = MealieClient(
            base_url=base_url,
            username=test_credentials["username"],
            password=test_credentials["password"]
        )
        
        await client.start_session()
        
        # Manually set expired token
        client.auth._access_token = "expired_token"
        client.auth._token_expires_at = datetime.now(UTC) - timedelta(hours=1)
        
        assert client.auth.needs_refresh is True
        
        await client.close_session()

    @pytest.mark.integration
    async def test_token_refresh_mechanism(self, integration_httpx_mock, base_url, test_credentials, auth_token_scenarios):
        """Test automatic token refresh mechanism."""
        # Initial login
        integration_httpx_mock.post("/api/auth/token").mock(
            return_value=httpx.Response(200, json=auth_token_scenarios["valid_token"])
        )
        
        # Mock refresh endpoint
        integration_httpx_mock.post("/api/auth/refresh").mock(
            return_value=httpx.Response(200, json={
                "access_token": "refreshed_access_token",
                "refresh_token": "refreshed_refresh_token",
                "token_type": "bearer",
                "expires_in": 3600
            })
        )
        
        client = MealieClient(
            base_url=base_url,
            username=test_credentials["username"],
            password=test_credentials["password"]
        )
        
        await client.start_session()
        
        # Force token to need refresh
        client.auth._token_expires_at = datetime.now(UTC) + timedelta(minutes=2)  # Within buffer
        
        # Request should trigger refresh
        await client.auth.get_auth_headers()
        
        # Verify refresh was called and tokens updated
        refresh_calls = [call for call in integration_httpx_mock.calls if "/api/auth/refresh" in str(call.request.url)]
        assert len(refresh_calls) > 0
        
        await client.close_session()

    @pytest.mark.integration
    async def test_concurrent_token_refresh(self, integration_httpx_mock, base_url, test_credentials):
        """Test that concurrent requests don't trigger multiple refreshes."""
        refresh_call_count = 0
        
        def refresh_side_effect(*args, **kwargs):
            nonlocal refresh_call_count
            refresh_call_count += 1
            return httpx.Response(200, json={
                "access_token": f"refreshed_token_{refresh_call_count}",
                "refresh_token": f"refreshed_refresh_{refresh_call_count}",
                "token_type": "bearer",
                "expires_in": 3600
            })
        
        integration_httpx_mock.post("/api/auth/token").mock(
            return_value=httpx.Response(200, json={
                "access_token": "initial_token",
                "refresh_token": "initial_refresh",
                "token_type": "bearer",
                "expires_in": 3600
            })
        )
        
        integration_httpx_mock.post("/api/auth/refresh").mock(side_effect=refresh_side_effect)
        
        client = MealieClient(
            base_url=base_url,
            username=test_credentials["username"],
            password=test_credentials["password"]
        )
        
        await client.start_session()
        
        # Force refresh needed
        client.auth._token_expires_at = datetime.now(UTC) - timedelta(minutes=1)
        
        # Make concurrent requests
        tasks = [
            client.auth.get_auth_headers(),
            client.auth.get_auth_headers(),
            client.auth.get_auth_headers()
        ]
        
        await asyncio.gather(*tasks)
        
        # Should only refresh once due to locking
        assert refresh_call_count == 1
        
        await client.close_session()


class TestLogoutAndCleanup:
    """Test suite for logout and authentication cleanup."""

    @pytest.mark.integration
    async def test_manual_logout(self, integration_httpx_mock, base_url, test_credentials):
        """Test manual logout clears authentication state."""
        integration_httpx_mock.post("/api/auth/token").mock(
            return_value=httpx.Response(200, json={
                "access_token": "logout_test_token",
                "refresh_token": "logout_test_refresh",
                "token_type": "bearer",
                "expires_in": 3600
            })
        )
        
        # Mock logout endpoint
        integration_httpx_mock.post("/api/auth/logout").mock(
            return_value=httpx.Response(200, json={"message": "Logged out successfully"})
        )
        
        client = MealieClient(
            base_url=base_url,
            username=test_credentials["username"],
            password=test_credentials["password"]
        )
        
        await client.start_session()
        
        # Verify authenticated
        assert client.auth.is_authenticated is True
        assert client.auth._access_token is not None
        
        # Logout
        await client.logout()
        
        # Verify cleared
        assert client.auth._access_token is None
        assert client.auth._refresh_token is None
        assert client.auth._token_expires_at is None
        
        await client.close_session()

    @pytest.mark.integration
    async def test_logout_with_token_revocation(self, integration_httpx_mock, base_url, test_credentials):
        """Test logout attempts to revoke refresh token."""
        integration_httpx_mock.post("/api/auth/token").mock(
            return_value=httpx.Response(200, json={
                "access_token": "revoke_test_token",
                "refresh_token": "revoke_test_refresh",
                "token_type": "bearer",
                "expires_in": 3600
            })
        )
        
        # Mock token revocation endpoint  
        integration_httpx_mock.delete("/api/auth/refresh").mock(
            return_value=httpx.Response(200, json={"message": "Token revoked"})
        )
        
        client = MealieClient(
            base_url=base_url,
            username=test_credentials["username"],
            password=test_credentials["password"]
        )
        
        await client.start_session()
        await client.logout()
        
        # Verify revocation was attempted
        revoke_calls = [call for call in integration_httpx_mock.calls if call.request.method == "DELETE"]
        assert len(revoke_calls) > 0
        
        await client.close_session()

    @pytest.mark.integration
    async def test_logout_handles_revocation_error(self, integration_httpx_mock, base_url, test_credentials):
        """Test logout continues even if token revocation fails."""
        integration_httpx_mock.post("/api/auth/token").mock(
            return_value=httpx.Response(200, json={
                "access_token": "error_test_token",
                "refresh_token": "error_test_refresh",
                "token_type": "bearer",
                "expires_in": 3600
            })
        )
        
        # Mock revocation failure
        integration_httpx_mock.delete("/api/auth/refresh").mock(
            return_value=httpx.Response(500, json={"error": "Server error"})
        )
        
        client = MealieClient(
            base_url=base_url,
            username=test_credentials["username"],
            password=test_credentials["password"]
        )
        
        await client.start_session()
        
        # Logout should succeed despite revocation error
        await client.logout()
        
        # Authentication should still be cleared
        assert client.auth._access_token is None
        assert client.auth._refresh_token is None
        
        await client.close_session()

    @pytest.mark.integration
    async def test_session_close_triggers_logout(self, integration_httpx_mock, base_url, test_credentials):
        """Test that closing session triggers logout for username/password auth."""
        integration_httpx_mock.post("/api/auth/token").mock(
            return_value=httpx.Response(200, json={
                "access_token": "session_close_token",
                "refresh_token": "session_close_refresh",
                "token_type": "bearer",
                "expires_in": 3600
            })
        )
        
        integration_httpx_mock.delete("/api/auth/refresh").mock(
            return_value=httpx.Response(200, json={"message": "Token revoked"})
        )
        
        client = MealieClient(
            base_url=base_url,
            username=test_credentials["username"],
            password=test_credentials["password"]
        )
        
        await client.start_session()
        assert client.auth._access_token is not None
        
        await client.close_session()
        
        # Should have cleared auth state
        assert client.auth._access_token is None


class TestAuthenticationErrors:
    """Test suite for authentication error scenarios."""

    @pytest.mark.integration
    async def test_network_error_during_login(self, integration_httpx_mock, base_url, test_credentials):
        """Test handling of network errors during login."""
        integration_httpx_mock.post("/api/auth/token").mock(
            side_effect=httpx.ConnectError("Connection failed")
        )
        
        client = MealieClient(
            base_url=base_url,
            username=test_credentials["username"],
            password=test_credentials["password"]
        )
        
        with pytest.raises((ConnectionError, httpx.ConnectError)):
            await client.start_session()

    @pytest.mark.integration
    async def test_server_error_during_login(self, integration_httpx_mock, base_url, test_credentials):
        """Test handling of server errors during login."""
        integration_httpx_mock.post("/api/auth/token").mock(
            return_value=httpx.Response(500, json={"error": "Internal server error"})
        )
        
        client = MealieClient(
            base_url=base_url,
            username=test_credentials["username"],
            password=test_credentials["password"]
        )
        
        with pytest.raises(AuthenticationError) as exc_info:
            await client.start_session()
        
        assert exc_info.value.status_code == 500

    @pytest.mark.integration
    async def test_malformed_login_response(self, integration_httpx_mock, base_url, test_credentials):
        """Test handling of malformed login responses."""
        integration_httpx_mock.post("/api/auth/token").mock(
            return_value=httpx.Response(200, json={"invalid": "response"})
        )
        
        client = MealieClient(
            base_url=base_url,
            username=test_credentials["username"],
            password=test_credentials["password"]
        )
        
        with pytest.raises((AuthenticationError, KeyError)):
            await client.start_session()

    @pytest.mark.integration
    async def test_auth_header_generation_without_login(self, base_url, test_credentials):
        """Test error when trying to get auth headers without login."""
        auth = MealieAuth(
            base_url=base_url,
            username=test_credentials["username"],
            password=test_credentials["password"]
        )
        
        with pytest.raises(AuthenticationError):
            await auth.get_auth_headers()

    @pytest.mark.integration
    async def test_invalid_token_response_structure(self, integration_httpx_mock, base_url, test_credentials):
        """Test handling of responses with invalid token structure."""
        integration_httpx_mock.post("/api/auth/token").mock(
            return_value=httpx.Response(200, text="not json")
        )
        
        client = MealieClient(
            base_url=base_url,
            username=test_credentials["username"],
            password=test_credentials["password"]
        )
        
        with pytest.raises((AuthenticationError, ValueError)):
            await client.start_session()


class TestEnvironmentAuthentication:
    """Test suite for environment-based authentication."""

    @pytest.mark.integration
    def test_from_env_with_username_password(self, base_url, monkeypatch):
        """Test creating client from environment with username/password."""
        # Only set username/password, not API token
        monkeypatch.setenv("MEALIE_USERNAME", "test_user")
        monkeypatch.setenv("MEALIE_PASSWORD", "test_password")
        
        client = MealieClient.from_env(base_url=base_url)
        
        assert client.auth.username == "test_user"
        assert client.auth.password == "test_password"
        assert client.auth.is_token_auth is False

    @pytest.mark.integration
    def test_from_env_with_api_token(self, base_url, monkeypatch):
        """Test creating client from environment with API token."""
        monkeypatch.setenv("MEALIE_API_TOKEN", "env_api_token_123")
        
        client = MealieClient.from_env(base_url=base_url)
        
        assert client.auth.api_token == "env_api_token_123"
        assert client.auth.is_token_auth is True

    @pytest.mark.integration
    def test_from_env_token_precedence(self, base_url, monkeypatch):
        """Test that API token takes precedence over username/password in env."""
        monkeypatch.setenv("MEALIE_USERNAME", "env_user")
        monkeypatch.setenv("MEALIE_PASSWORD", "env_pass")
        monkeypatch.setenv("MEALIE_API_TOKEN", "env_token_123")
        
        client = MealieClient.from_env(base_url=base_url)
        
        # Should use token, not username/password
        assert client.auth.api_token == "env_token_123"
        assert client.auth.is_token_auth is True

    @pytest.mark.integration
    def test_from_env_custom_variable_names(self, base_url, monkeypatch):
        """Test custom environment variable names."""
        monkeypatch.setenv("CUSTOM_USER", "custom_user")
        monkeypatch.setenv("CUSTOM_PASS", "custom_pass")
        
        auth = MealieAuth(
            base_url=base_url,
            username_env="CUSTOM_USER",
            password_env="CUSTOM_PASS"
        )
        
        # Note: This would require modifying create_auth_from_env to accept custom env var names
        # For now, just test that the concept works with direct auth creation
        assert auth.username == "custom_user"
        assert auth.password == "custom_pass"


class TestAuthenticationIntegrationWithRequests:
    """Test suite for authentication integration with HTTP requests."""

    @pytest.mark.integration
    async def test_authenticated_request_includes_headers(self, integration_httpx_mock, base_url, test_credentials):
        """Test that authenticated requests include proper headers."""
        integration_httpx_mock.post("/api/auth/token").mock(
            return_value=httpx.Response(200, json={
                "access_token": "request_test_token",
                "refresh_token": "request_test_refresh",
                "token_type": "bearer",
                "expires_in": 3600
            })
        )
        
        integration_httpx_mock.get("/api/recipes").mock(
            return_value=httpx.Response(200, json={"items": []})
        )
        
        client = MealieClient(
            base_url=base_url,
            username=test_credentials["username"],
            password=test_credentials["password"]
        )
        
        await client.start_session()
        await client.get("recipes")
        
        # Verify auth header was included
        recipe_request = integration_httpx_mock.calls[-1].request
        assert "Authorization" in recipe_request.headers
        assert recipe_request.headers["Authorization"] == "Bearer request_test_token"
        
        await client.close_session()

    @pytest.mark.integration
    async def test_unauthenticated_request_option(self, integration_httpx_mock, base_url, test_credentials):
        """Test making unauthenticated requests when needed."""
        integration_httpx_mock.get("/api/app/about").mock(
            return_value=httpx.Response(200, json={"status": "ok"})
        )
        
        client = MealieClient(
            base_url=base_url,
            username=test_credentials["username"],
            password=test_credentials["password"]
        )
        
        await client.start_session()
        await client.get("app/about", authenticated=False)
        
        # Verify no auth header was included
        about_request = integration_httpx_mock.calls[-1].request
        assert "Authorization" not in about_request.headers
        
        await client.close_session() 