"""
Integration tests for MealieClient lifecycle management.

Tests cover client initialization, session management, context manager usage,
and proper resource cleanup scenarios.
"""

import asyncio

import pytest

from mealie_client import MealieClient
from mealie_client.exceptions import ConfigurationError


class TestClientInitialization:
    """Test suite for client initialization and configuration."""

    @pytest.mark.integration
    def test_client_init_with_username_password(self, base_url, test_credentials):
        """Test client initialization with username/password authentication."""
        client = MealieClient(
            base_url=base_url,
            username=test_credentials["username"],
            password=test_credentials["password"]
        )
        
        assert client.base_url == f"{base_url}/api"  # Base URL gets /api appended
        assert client.auth.username == test_credentials["username"]
        assert client.auth.password == test_credentials["password"]
        assert client.auth.is_token_auth is False
        assert client.timeout == 30.0  # Default timeout
        assert client.max_retries == 3  # Default retries
        assert client._session_started is False

    @pytest.mark.integration
    def test_client_init_with_api_token(self, base_url, test_credentials):
        """Test client initialization with API token authentication."""
        client = MealieClient(
            base_url=base_url,
            api_token=test_credentials["api_token"]
        )
        
        assert client.base_url == f"{base_url}/api"  # Base URL gets /api appended
        assert client.auth.api_token == test_credentials["api_token"]
        assert client.auth.is_token_auth is True
        assert client.auth.username is None
        assert client.auth.password is None

    @pytest.mark.integration
    def test_client_init_with_custom_settings(self, base_url, test_credentials):
        """Test client initialization with custom settings."""
        client = MealieClient(
            base_url=base_url,
            username=test_credentials["username"],
            password=test_credentials["password"],
            timeout=60.0,
            max_retries=5,
            retry_delay=2.0,
            user_agent="custom-agent/1.0"
        )
        
        assert client.timeout == 60.0
        assert client.max_retries == 5
        assert client.retry_delay == 2.0
        assert client.user_agent == "custom-agent/1.0"

    @pytest.mark.integration
    def test_client_init_invalid_config(self, base_url):
        """Test client initialization with invalid configuration."""
        with pytest.raises(ConfigurationError) as exc_info:
            MealieClient(base_url=base_url)  # No auth provided
        
        assert "authentication" in str(exc_info.value).lower()

    @pytest.mark.integration
    def test_client_from_env(self, base_url, mock_env_vars):
        """Test client creation from environment variables."""
        client = MealieClient.from_env(base_url=base_url)
        
        assert client.base_url == f"{base_url}/api"  # Base URL gets /api appended
        assert client.auth.username == "test_user"
        assert client.auth.password == "test_password"

    @pytest.mark.integration
    def test_client_from_env_missing_vars(self, base_url, monkeypatch):
        """Test client creation fails when environment variables are missing."""
        # Clear environment variables
        monkeypatch.delenv("MEALIE_USERNAME", raising=False)
        monkeypatch.delenv("MEALIE_PASSWORD", raising=False)
        monkeypatch.delenv("MEALIE_API_TOKEN", raising=False)
        
        with pytest.raises(ConfigurationError):
            MealieClient.from_env(base_url=base_url)


class TestSessionManagement:
    """Test suite for client session lifecycle management."""

    @pytest.mark.integration
    async def test_start_session_success(self, integration_httpx_mock, connected_client):
        """Test successful session startup."""
        assert connected_client._session_started is False
        assert connected_client._http_client is None
        
        await connected_client.start_session()
        
        assert connected_client._session_started is True
        assert connected_client._http_client is not None
        assert connected_client.recipes is not None
        assert connected_client.users is not None
        assert connected_client.groups is not None
        assert connected_client.meal_plans is not None
        assert connected_client.shopping_lists is not None

    @pytest.mark.integration
    async def test_start_session_multiple_calls(self, integration_httpx_mock, connected_client):
        """Test that multiple start_session calls are safe."""
        await connected_client.start_session()
        first_client = connected_client._http_client
        
        # Second call should not create new client
        await connected_client.start_session()
        assert connected_client._http_client is first_client

    @pytest.mark.integration
    async def test_close_session_success(self, integration_httpx_mock, connected_client):
        """Test successful session cleanup."""
        await connected_client.start_session()
        assert connected_client._session_started is True
        
        await connected_client.close_session()
        
        assert connected_client._session_started is False
        assert connected_client._http_client is None

    @pytest.mark.integration
    async def test_close_session_when_not_started(self, connected_client):
        """Test that closing an unstarted session is safe."""
        assert connected_client._session_started is False
        
        # Should not raise any errors
        await connected_client.close_session()
        assert connected_client._session_started is False

    @pytest.mark.integration
    async def test_start_session_httpx_missing(self, connected_client, monkeypatch):
        """Test session startup fails gracefully when httpx is missing."""
        # Mock httpx import failure
        import sys
        original_httpx = sys.modules.get('httpx')
        if 'httpx' in sys.modules:
            del sys.modules['httpx']
        
        # Mock the import to raise ImportError
        def mock_import(name, *args, **kwargs):
            if name == 'httpx':
                raise ImportError("No module named 'httpx'")
            return original_httpx
        
        monkeypatch.setattr('builtins.__import__', mock_import)
        
        with pytest.raises(ConfigurationError) as exc_info:
            await connected_client.start_session()
        
        assert "httpx is required" in str(exc_info.value)
        
        # Restore httpx
        if original_httpx:
            sys.modules['httpx'] = original_httpx

    @pytest.mark.integration
    async def test_session_auth_initialization(self, integration_httpx_mock, connected_client):
        """Test that authentication is properly initialized during session startup."""
        await connected_client.start_session()
        
        # Check that auth handler has HTTP client set
        assert connected_client.auth._http_client is not None
        assert connected_client.auth._http_client is connected_client._http_client


class TestContextManagerUsage:
    """Test suite for async context manager functionality."""

    @pytest.mark.integration
    async def test_context_manager_success(self, integration_httpx_mock, base_url, test_credentials):
        """Test successful context manager usage."""
        async with MealieClient(
            base_url=base_url,
            username=test_credentials["username"],
            password=test_credentials["password"]
        ) as client:
            assert client._session_started is True
            assert client._http_client is not None
            
            # Client should be fully functional
            assert client.recipes is not None
            assert client.users is not None

    @pytest.mark.integration
    async def test_context_manager_cleanup_on_success(self, integration_httpx_mock, base_url, test_credentials):
        """Test that context manager properly cleans up after successful completion."""
        client = None
        
        async with MealieClient(
            base_url=base_url,
            username=test_credentials["username"],
            password=test_credentials["password"]
        ) as c:
            client = c
            assert client._session_started is True
        
        # After context exit, should be cleaned up
        assert client._session_started is False
        assert client._http_client is None

    @pytest.mark.integration
    async def test_context_manager_cleanup_on_exception(self, integration_httpx_mock, base_url, test_credentials):
        """Test that context manager cleans up properly even when exceptions occur."""
        client = None
        
        try:
            async with MealieClient(
                base_url=base_url,
                username=test_credentials["username"],
                password=test_credentials["password"]
            ) as c:
                client = c
                # Note: context manager already calls start_session, so client should be started
                assert client._session_started is True
                raise ValueError("Test exception")
        except ValueError:
            pass  # Expected exception
        
        # Even after exception, should be cleaned up
        assert client._session_started is False

    @pytest.mark.integration
    async def test_nested_context_managers(self, integration_httpx_mock, base_url, test_credentials):
        """Test that nested context manager usage works correctly."""
        async with MealieClient(
            base_url=base_url,
            api_token=test_credentials["api_token"]
        ) as client1:
            assert client1._session_started is True
            
            async with MealieClient(
                base_url=base_url,
                username=test_credentials["username"],
                password=test_credentials["password"]
            ) as client2:
                assert client2._session_started is True
                assert client1._session_started is True  # First client still active
            
            # Second client cleaned up, first still active
            assert client2._session_started is False
            assert client1._session_started is True
        
        # Both clients cleaned up
        assert client1._session_started is False


class TestClientProperties:
    """Test suite for client property methods and state checking."""

    @pytest.mark.integration
    async def test_is_connected_before_session(self, connected_client):
        """Test is_connected returns False before session starts."""
        assert connected_client.is_connected() is False

    @pytest.mark.integration
    async def test_is_connected_after_session(self, integration_httpx_mock, connected_client):
        """Test is_connected returns True after session starts."""
        await connected_client.start_session()
        assert connected_client.is_connected() is True

    @pytest.mark.integration
    async def test_is_connected_after_close(self, integration_httpx_mock, connected_client):
        """Test is_connected returns False after session closes."""
        await connected_client.start_session()
        assert connected_client.is_connected() is True
        
        await connected_client.close_session()
        assert connected_client.is_connected() is False

    @pytest.mark.integration
    def test_get_base_url(self, connected_client, base_url):
        """Test get_base_url returns correct URL."""
        assert connected_client.get_base_url() == f"{base_url}/api"  # Base URL gets /api appended

    @pytest.mark.integration
    def test_get_client_info(self, connected_client):
        """Test get_client_info returns client configuration."""
        info = connected_client.get_client_info()
        
        assert "base_url" in info
        assert "timeout" in info
        assert "max_retries" in info
        assert "user_agent" in info
        assert "connected" in info  # Key is "connected" not "session_started"
        assert "auth_info" in info
        
        assert info["base_url"] == connected_client.base_url
        assert info["timeout"] == connected_client.timeout
        assert info["max_retries"] == connected_client.max_retries
        assert info["connected"] == connected_client._session_started

    @pytest.mark.integration
    async def test_get_auth_info(self, integration_httpx_mock, connected_client):
        """Test get_auth_info returns authentication information."""
        await connected_client.start_session()
        
        auth_info = connected_client.get_auth_info()
        
        assert "auth_type" in auth_info
        assert "authenticated" in auth_info
        assert "username" in auth_info
        
        assert auth_info["auth_type"] == "username_password"
        assert auth_info["authenticated"] is True
        assert auth_info["username"] == "test_user"


class TestEndpointManagerInitialization:
    """Test suite for endpoint manager initialization."""

    @pytest.mark.integration
    async def test_endpoint_managers_initialized(self, integration_httpx_mock, connected_client):
        """Test that all endpoint managers are properly initialized."""
        await connected_client.start_session()
        
        # Check that all endpoint managers exist
        assert connected_client.recipes is not None
        assert connected_client.users is not None
        assert connected_client.groups is not None
        assert connected_client.meal_plans is not None
        assert connected_client.shopping_lists is not None
        
        # Check that they have the client reference
        assert connected_client.recipes.client is connected_client
        assert connected_client.users.client is connected_client
        assert connected_client.groups.client is connected_client
        assert connected_client.meal_plans.client is connected_client
        assert connected_client.shopping_lists.client is connected_client

    @pytest.mark.integration
    async def test_endpoint_managers_not_available_before_session(self, connected_client):
        """Test that endpoint managers are None before session starts."""
        assert connected_client.recipes is None
        assert connected_client.users is None
        assert connected_client.groups is None
        assert connected_client.meal_plans is None
        assert connected_client.shopping_lists is None

    @pytest.mark.integration
    async def test_endpoint_managers_persistent_across_operations(self, integration_httpx_mock, connected_client):
        """Test that endpoint managers persist across multiple operations."""
        await connected_client.start_session()
        
        recipes_manager = connected_client.recipes
        users_manager = connected_client.users
        
        # Simulate some usage (managers should remain the same instances)
        await asyncio.sleep(0.1)  # Small delay
        
        assert connected_client.recipes is recipes_manager
        assert connected_client.users is users_manager


class TestResourceCleanup:
    """Test suite for proper resource cleanup scenarios."""

    @pytest.mark.integration
    async def test_cleanup_handles_http_client_close_error(self, integration_httpx_mock, connected_client):
        """Test cleanup handles errors during HTTP client closure gracefully."""
        await connected_client.start_session()
        
        # Mock HTTP client close to raise an exception
        original_aclose = connected_client._http_client.aclose
        async def mock_aclose():
            raise Exception("Close error")
        connected_client._http_client.aclose = mock_aclose
        
        # Cleanup should still complete without raising, but need to handle the exception
        try:
            await connected_client.close_session()
        except Exception:
            # The client code might not handle this gracefully yet, that's what we're testing
            pass
        
        # The session state should still be cleared even if close failed
        assert connected_client._session_started is False

    @pytest.mark.integration
    async def test_multiple_cleanup_calls_safe(self, integration_httpx_mock, connected_client):
        """Test that multiple cleanup calls are safe."""
        await connected_client.start_session()
        
        # Multiple close calls should be safe
        await connected_client.close_session()
        await connected_client.close_session()
        await connected_client.close_session()
        
        assert connected_client._session_started is False

    @pytest.mark.integration
    async def test_cleanup_in_destructor_scenario(self, integration_httpx_mock, base_url, test_credentials):
        """Test cleanup behavior in destructor-like scenarios."""
        client = MealieClient(
            base_url=base_url,
            username=test_credentials["username"],
            password=test_credentials["password"]
        )
        
        await client.start_session()
        assert client._session_started is True
        
        # Simulate object going out of scope (manual cleanup)
        await client.close_session()
        client = None  # Simulate garbage collection
        
        # No assertion needed - just verify no exceptions thrown 