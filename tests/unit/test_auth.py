"""
Unit tests for Mealie SDK authentication functionality.

Tests cover MealieAuth class initialization, token management,
authentication flows, and environment variable configuration.
"""

from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, Mock

import pytest

from mealie_client.auth import MealieAuth, AuthenticationManager, create_auth_from_env
from mealie_client.exceptions import (
    AuthenticationError,
    ConfigurationError
)


class TestMealieAuth:
    """Test suite for MealieAuth class."""

    @pytest.mark.unit
    def test_init_with_username_password(self, base_url, test_credentials):
        """Test MealieAuth initialization with username/password."""
        auth = MealieAuth(
            base_url=base_url,
            username=test_credentials["username"],
            password=test_credentials["password"]
        )
        
        assert auth.base_url == base_url
        assert auth.username == test_credentials["username"]
        assert auth.password == test_credentials["password"]
        assert auth.api_token is None
        assert not auth.is_token_auth
        assert auth.auto_refresh is True
        assert auth.token_buffer_minutes == 5

    @pytest.mark.unit
    def test_init_with_api_token(self, base_url, test_credentials):
        """Test MealieAuth initialization with API token."""
        auth = MealieAuth(
            base_url=base_url,
            api_token=test_credentials["api_token"]
        )
        
        assert auth.base_url == base_url
        assert auth.api_token == test_credentials["api_token"]
        assert auth.username is None
        assert auth.password is None
        assert auth.is_token_auth is True

    # TODO: Implement this test
    @pytest.mark.skip(reason="TODO: Implement this test")
    def test_init_without_credentials_raises_error(self, base_url):
        """Test that initialization without credentials raises ConfigurationError."""
        with pytest.raises(ConfigurationError) as exc_info:
            MealieAuth(base_url=base_url)
        
        assert "Either api_token or both username and password must be provided" in str(exc_info.value)
        assert exc_info.value.config_field == "authentication"

    @pytest.mark.unit
    def test_init_with_partial_credentials_raises_error(self, base_url):
        """Test that initialization with only username raises ConfigurationError."""
        with pytest.raises(ConfigurationError):
            MealieAuth(
                base_url=base_url,
                username="test_user"
                # Missing password
            )

    @pytest.mark.unit
    async def test_get_auth_headers_with_api_token(self, mealie_auth_token, test_credentials):
        """Test authentication headers with API token."""
        headers = await mealie_auth_token.get_auth_headers()
        
        expected = f"Bearer {test_credentials['api_token']}"
        assert headers["Authorization"] == expected

    # TODO: Implement this test
    @pytest.mark.skip(reason="TODO: Implement this test")
    async def test_get_auth_headers_without_access_token_raises_error(self, mealie_auth):
        """Test that get_auth_headers raises error when no access token available."""
        # No HTTP client set, so login can't work
        with pytest.raises(AuthenticationError) as exc_info:
            await mealie_auth.get_auth_headers()
        
        assert "No valid access token available" in str(exc_info.value)

    @pytest.mark.unit
    async def test_perform_login_success(self, mealie_auth, auth_token_response):
        """Test successful login flow."""
        # Mock HTTP client
        mock_client = AsyncMock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = auth_token_response
        mock_client.post.return_value = mock_response
        
        mealie_auth.set_http_client(mock_client)
        
        await mealie_auth._perform_login()
        
        # Verify the login request was made correctly
        mock_client.post.assert_called_once()
        call_args = mock_client.post.call_args
        assert "/auth/token" in call_args[0][0]
        assert call_args[1]["data"]["username"] == mealie_auth.username
        assert call_args[1]["data"]["password"] == mealie_auth.password
        
        # Verify tokens were stored
        assert mealie_auth._access_token == auth_token_response["access_token"]
        assert mealie_auth._refresh_token == auth_token_response["refresh_token"]
        assert mealie_auth._token_expires_at is not None

    @pytest.mark.unit
    async def test_perform_login_invalid_credentials(self, mealie_auth):
        """Test login with invalid credentials."""
        # Mock HTTP client with 401 response
        mock_client = AsyncMock()
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {"detail": "Invalid credentials"}
        mock_response.content = True
        mock_client.post.return_value = mock_response
        
        mealie_auth.set_http_client(mock_client)
        
        with pytest.raises(AuthenticationError) as exc_info:
            await mealie_auth._perform_login()
        
        assert exc_info.value.status_code == 401
        assert "Invalid username or password" in str(exc_info.value)

    @pytest.mark.unit
    async def test_perform_login_server_error(self, mealie_auth):
        """Test login with server error."""
        # Mock HTTP client with 500 response
        mock_client = AsyncMock()
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.json.return_value = {"detail": "Internal server error"}
        mock_response.content = True
        mock_client.post.return_value = mock_response
        
        mealie_auth.set_http_client(mock_client)
        
        with pytest.raises(AuthenticationError) as exc_info:
            await mealie_auth._perform_login()
        
        assert exc_info.value.status_code == 500

    @pytest.mark.unit
    async def test_refresh_token_success(self, mealie_auth):
        """Test successful token refresh."""
        # Set up existing tokens
        mealie_auth._refresh_token = "old_refresh_token"
        
        # Mock HTTP client
        mock_client = AsyncMock()
        mock_response = Mock()
        mock_response.status_code = 200
        new_token_data = {
            "access_token": "new_access_token",
            "refresh_token": "new_refresh_token",
            "expires_in": 3600
        }
        mock_response.json.return_value = new_token_data
        mock_client.post.return_value = mock_response
        
        mealie_auth.set_http_client(mock_client)
        
        await mealie_auth._refresh_auth()
        
        # Verify refresh request was made
        mock_client.post.assert_called_once()
        call_args = mock_client.post.call_args
        assert "/auth/refresh" in call_args[0][0]
        
        # Verify new tokens were stored
        assert mealie_auth._access_token == "new_access_token"
        assert mealie_auth._refresh_token == "new_refresh_token"

    @pytest.mark.unit
    async def test_refresh_token_failure_triggers_relogin(self, mealie_auth, auth_token_response):
        """Test that failed token refresh triggers a new login."""
        mealie_auth._refresh_token = "expired_refresh_token"
        
        # Mock HTTP client
        mock_client = AsyncMock()
        
        # First call (refresh) returns 401, second call (login) succeeds
        mock_refresh_response = Mock()
        mock_refresh_response.status_code = 401
        mock_refresh_response.json.return_value = {"detail": "Invalid refresh token"}
        mock_refresh_response.content = True
        
        mock_login_response = Mock()
        mock_login_response.status_code = 200
        mock_login_response.json.return_value = auth_token_response
        
        mock_client.post.side_effect = [mock_refresh_response, mock_login_response]
        mealie_auth.set_http_client(mock_client)
        
        await mealie_auth._refresh_auth()
        
        # Verify both refresh and login were called
        assert mock_client.post.call_count == 2
        
        # Verify tokens from login were stored
        assert mealie_auth._access_token == auth_token_response["access_token"]

    @pytest.mark.unit
    def test_needs_refresh_true_when_token_near_expiry(self, mealie_auth):
        """Test that needs_refresh returns True when token is near expiry."""
        # Set token to expire in 2 minutes (less than buffer of 5 minutes)
        near_expiry = datetime.now(UTC) + timedelta(minutes=2)
        mealie_auth._token_expires_at = near_expiry
        
        assert mealie_auth.needs_refresh is True

    @pytest.mark.unit
    def test_needs_refresh_false_when_token_not_near_expiry(self, mealie_auth):
        """Test that needs_refresh returns False when token is not near expiry."""
        # Set token to expire in 10 minutes (more than buffer of 5 minutes)
        future_expiry = datetime.now(UTC) + timedelta(minutes=10)
        mealie_auth._token_expires_at = future_expiry
        
        assert mealie_auth.needs_refresh is False

    @pytest.mark.unit
    def test_needs_refresh_false_for_api_token_auth(self, mealie_auth_token):
        """Test that needs_refresh returns False for API token authentication."""
        assert mealie_auth_token.needs_refresh is False

    @pytest.mark.unit
    async def test_logout_clears_tokens(self, mealie_auth):
        """Test that logout clears authentication state."""
        # Set up existing tokens
        mealie_auth._access_token = "test_token"
        mealie_auth._refresh_token = "test_refresh"
        mealie_auth._token_expires_at = datetime.now(UTC) + timedelta(hours=1)
        
        # Mock HTTP client
        mock_client = AsyncMock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_client.post.return_value = mock_response
        mealie_auth.set_http_client(mock_client)
        
        await mealie_auth.logout()
        
        # Verify tokens were cleared
        assert mealie_auth._access_token is None
        assert mealie_auth._refresh_token is None
        assert mealie_auth._token_expires_at is None

    @pytest.mark.unit
    async def test_logout_handles_revocation_failure_gracefully(self, mealie_auth):
        """Test that logout handles token revocation failure gracefully."""
        mealie_auth._refresh_token = "test_refresh"
        
        # Mock HTTP client that fails revocation
        mock_client = AsyncMock()
        mock_client.post.side_effect = Exception("Network error")
        mealie_auth.set_http_client(mock_client)
        
        # Should not raise exception
        await mealie_auth.logout()
        
        # Tokens should still be cleared
        assert mealie_auth._access_token is None
        assert mealie_auth._refresh_token is None

    @pytest.mark.unit
    def test_is_authenticated_true_with_api_token(self, mealie_auth_token):
        """Test is_authenticated returns True for API token auth."""
        assert mealie_auth_token.is_authenticated is True

    @pytest.mark.unit
    def test_is_authenticated_true_with_access_token(self, mealie_auth):
        """Test is_authenticated returns True when access token is present."""
        mealie_auth._access_token = "test_token"
        assert mealie_auth.is_authenticated is True

    @pytest.mark.unit
    def test_is_authenticated_false_without_tokens(self, mealie_auth):
        """Test is_authenticated returns False when no tokens present."""
        assert mealie_auth.is_authenticated is False


class TestAuthenticationManager:
    """Test suite for AuthenticationManager class."""

    @pytest.mark.unit
    def test_init(self):
        """Test AuthenticationManager initialization."""
        manager = AuthenticationManager()
        assert len(manager._auth_handlers) == 0
        assert manager._default_handler is None

    @pytest.mark.unit
    def test_add_auth_with_username_password(self, base_url, test_credentials):
        """Test adding auth handler with username/password."""
        manager = AuthenticationManager()
        
        auth = manager.add_auth(
            name="test",
            base_url=base_url,
            username=test_credentials["username"],
            password=test_credentials["password"]
        )
        
        assert isinstance(auth, MealieAuth)
        assert auth.username == test_credentials["username"]
        assert "test" in manager._auth_handlers
        assert manager._default_handler == "test"

    @pytest.mark.unit
    def test_add_auth_with_api_token(self, base_url, test_credentials):
        """Test adding auth handler with API token."""
        manager = AuthenticationManager()
        
        auth = manager.add_auth(
            name="token_auth",
            base_url=base_url,
            api_token=test_credentials["api_token"]
        )
        
        assert isinstance(auth, MealieAuth)
        assert auth.api_token == test_credentials["api_token"]
        assert "token_auth" in manager._auth_handlers
        assert manager._default_handler == "token_auth"

    @pytest.mark.unit
    def test_get_auth_by_name(self, base_url, test_credentials):
        """Test retrieving auth handler by name."""
        manager = AuthenticationManager()
        
        original_auth = manager.add_auth(
            name="test",
            base_url=base_url,
            username=test_credentials["username"],
            password=test_credentials["password"]
        )
        
        retrieved_auth = manager.get_auth("test")
        assert retrieved_auth == original_auth

    @pytest.mark.unit
    def test_get_auth_default(self, base_url, test_credentials):
        """Test retrieving default auth handler."""
        manager = AuthenticationManager()
        
        original_auth = manager.add_auth(
            name="test",
            base_url=base_url,
            username=test_credentials["username"],
            password=test_credentials["password"]
        )
        
        # Should return default when no name specified
        retrieved_auth = manager.get_auth()
        assert retrieved_auth == original_auth

    @pytest.mark.unit
    def test_get_auth_nonexistent_raises_error(self):
        """Test that getting nonexistent auth handler raises error."""
        manager = AuthenticationManager()
        
        with pytest.raises(ValueError) as exc_info:
            manager.get_auth("nonexistent")
        
        assert "Auth handler 'nonexistent' not found" in str(exc_info.value)

    @pytest.mark.unit
    def test_get_auth_no_default_raises_error(self):
        """Test that getting auth with no default raises error."""
        manager = AuthenticationManager()
        
        with pytest.raises(ValueError) as exc_info:
            manager.get_auth()
        
        assert "Auth handler 'None' not found" in str(exc_info.value)

    @pytest.mark.unit
    def test_set_default(self, base_url, test_credentials):
        """Test setting default auth handler."""
        manager = AuthenticationManager()
        
        manager.add_auth(
            name="first",
            base_url=base_url,
            username=test_credentials["username"],
            password=test_credentials["password"]
        )
        
        manager.add_auth(
            name="second",
            base_url=base_url,
            api_token=test_credentials["api_token"]
        )
        
        manager.set_default("second")
        assert manager._default_handler == "second"
        
        default_auth = manager.get_auth()
        assert default_auth.api_token == test_credentials["api_token"]

    @pytest.mark.unit
    def test_set_default_nonexistent_raises_error(self):
        """Test that setting nonexistent default raises error."""
        manager = AuthenticationManager()
        
        with pytest.raises(ValueError) as exc_info:
            manager.set_default("nonexistent")
        
        assert "Auth handler 'nonexistent' not found" in str(exc_info.value)

    @pytest.mark.unit
    def test_list_auth_handlers(self, base_url, test_credentials):
        """Test listing auth handler names."""
        manager = AuthenticationManager()
        
        manager.add_auth("first", base_url, username="user1", password="pass1")
        manager.add_auth("second", base_url, api_token="token123")
        
        handlers = manager.list_auth_handlers()
        assert set(handlers) == {"first", "second"}

    @pytest.mark.unit
    async def test_logout_all(self, base_url, test_credentials):
        """Test logging out all auth handlers."""
        manager = AuthenticationManager()
        
        # Add multiple auth handlers
        auth1 = manager.add_auth("first", base_url, username="user1", password="pass1")
        auth2 = manager.add_auth("second", base_url, api_token="token123")
        
        # Mock their logout methods
        auth1.logout = AsyncMock()
        auth2.logout = AsyncMock()
        
        await manager.logout_all()
        
        # Verify logout was called on all handlers
        auth1.logout.assert_called_once()
        auth2.logout.assert_called_once()


class TestCreateAuthFromEnv:
    """Test suite for create_auth_from_env function."""

    @pytest.mark.unit
    def test_create_auth_from_env_with_username_password(self, base_url, mock_env_vars):
        """Test creating auth from environment variables with username/password."""
        auth = create_auth_from_env(base_url)
        
        assert isinstance(auth, MealieAuth)
        assert auth.username == "test_user"
        assert auth.password == "test_password"
        assert auth.api_token is not None

    @pytest.mark.unit  
    def test_create_auth_from_env_with_api_token(self, base_url, monkeypatch):
        """Test creating auth from environment variables with API token."""
        # Set only API token
        monkeypatch.setenv("MEALIE_API_TOKEN", "test_token")
        
        auth = create_auth_from_env(base_url)
        
        assert isinstance(auth, MealieAuth)
        assert auth.api_token == "test_token"
        assert auth.username is None
        assert auth.password is None

    @pytest.mark.unit
    def test_create_auth_from_env_custom_var_names(self, base_url, monkeypatch):
        """Test creating auth with custom environment variable names."""
        monkeypatch.setenv("CUSTOM_USER", "custom_user")
        monkeypatch.setenv("CUSTOM_PASS", "custom_pass")
        
        auth = create_auth_from_env(
            base_url,
            username_env="CUSTOM_USER",
            password_env="CUSTOM_PASS"
        )
        
        assert auth.username == "custom_user"
        assert auth.password == "custom_pass"

    @pytest.mark.unit
    def test_create_auth_from_env_no_credentials_raises_error(self, base_url):
        """Test that missing environment variables raises ConfigurationError."""
        with pytest.raises(ConfigurationError) as exc_info:
            create_auth_from_env(base_url)
        
        assert "No authentication found in environment" in str(exc_info.value) 