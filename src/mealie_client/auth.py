"""
Authentication module for the Mealie SDK.

This module handles authentication with the Mealie API, including login,
token management, and automatic token refresh.
"""

import asyncio
from datetime import UTC, datetime, timedelta
from typing import Any, Dict, List, Optional, Union

from .exceptions import AuthenticationError, AuthorizationError, ConfigurationError
from .utils import build_url, generate_request_id


class MealieAuth:
    """
    Handles authentication with the Mealie API.
    
    Supports both username/password authentication and API token authentication.
    Automatically manages token refresh when using username/password.
    """

    def __init__(
        self,
        base_url: str,
        username: Optional[str] = None,
        password: Optional[str] = None,
        api_token: Optional[str] = None,
        auto_refresh: bool = True,
        token_buffer_minutes: int = 5,
        username_env: Optional[str] = None,
        password_env: Optional[str] = None,
    ) -> None:
        """
        Initialize authentication handler.

        Args:
            base_url: Base URL of the Mealie instance
            username: Username for login authentication
            password: Password for login authentication
            api_token: API token for token-based authentication
            auto_refresh: Whether to automatically refresh tokens
            token_buffer_minutes: Minutes before expiry to refresh token
            username_env: Environment variable name for username (for testing)
            password_env: Environment variable name for password (for testing)

        Raises:
            ConfigurationError: If neither credentials nor token provided
        """
        # Handle environment variable loading if custom names provided
        if username_env or password_env:
            import os
            if username_env and not username:
                username = os.getenv(username_env)
            if password_env and not password:
                password = os.getenv(password_env)
        self.base_url = base_url
        self.username = username
        self.password = password
        self.api_token = api_token
        self.auto_refresh = auto_refresh
        self.token_buffer_minutes = token_buffer_minutes

        # Internal state
        self._access_token: Optional[str] = None
        self._refresh_token: Optional[str] = None
        self._token_expires_at: Optional[datetime] = None
        self._lock = asyncio.Lock()
        self._http_client: Optional[Any] = None  # Will be set by client

        # Validate configuration
        self._validate_config()

    def _validate_config(self) -> None:
        """Validate authentication configuration."""
        if not self.api_token and not (self.username and self.password):
            raise ConfigurationError(
                "Either api_token or both username and password must be provided",
                config_field="authentication",
                expected_type="api_token or username/password",
            )

    def set_http_client(self, client: Any) -> None:
        """
        Set the HTTP client instance to use for requests.

        Args:
            client: HTTP client instance
        """
        self._http_client = client

    @property
    def is_token_auth(self) -> bool:
        """Check if using API token authentication."""
        # API token takes precedence over username/password
        return self.api_token is not None

    @property
    def is_authenticated(self) -> bool:
        """Check if currently authenticated."""
        if self.is_token_auth:
            return True
        return self._access_token is not None

    @property
    def needs_refresh(self) -> bool:
        """Check if token needs refresh."""
        if not self.auto_refresh or self.is_token_auth or not self._token_expires_at:
            return False

        buffer_time = timedelta(minutes=self.token_buffer_minutes)
        return datetime.now(UTC) + buffer_time >= self._token_expires_at

    async def get_auth_headers(self) -> Dict[str, str]:
        """
        Get authentication headers for API requests.

        Returns:
            Dictionary with authentication headers

        Raises:
            AuthenticationError: If authentication fails
        """
        async with self._lock:
            # Use API token if available
            if self.api_token:
                return {"Authorization": f"Bearer {self.api_token}"}

            # Ensure we have a valid access token
            if not self._access_token or self.needs_refresh:
                await self._refresh_auth()

            if not self._access_token:
                raise AuthenticationError("No valid access token available")

            return {"Authorization": f"Bearer {self._access_token}"}

    async def login(self) -> None:
        """
        Perform initial login with username/password.

        Raises:
            AuthenticationError: If login fails
            ConfigurationError: If credentials not provided
        """
        if not self.username or not self.password:
            raise ConfigurationError(
                "Username and password required for login",
                config_field="credentials",
            )

        await self._perform_login()

    async def logout(self) -> None:
        """
        Logout and clear authentication state.
        """
        async with self._lock:
            if self._refresh_token and self._http_client:
                # Attempt to revoke refresh token
                try:
                    await self._revoke_token()
                except Exception:
                    # Ignore revocation errors during logout
                    pass

            self._clear_tokens()

    async def refresh_token(self) -> None:
        """
        Manually refresh the access token.

        Raises:
            AuthenticationError: If refresh fails
        """
        if self.is_token_auth:
            return  # No refresh needed for API tokens

        async with self._lock:
            await self._refresh_auth()

    async def _perform_login(self) -> None:
        """Perform login request."""
        if not self._http_client:
            raise AuthenticationError("Authentication not initialized - start session first")

        url = build_url(self.base_url, "auth", "token")
        data = {
            "username": self.username,
            "password": self.password,
        }

        try:
            response = await self._http_client.post(
                url,
                data=data,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )

            if response.status_code == 200:
                token_data = response.json()
                self._store_tokens(token_data)
            elif response.status_code == 401:
                raise AuthenticationError(
                    "Invalid username or password",
                    status_code=response.status_code,
                    response_data=response.json() if response.content else None,
                )
            else:
                response_data = response.json() if response.content else None
                raise AuthenticationError(
                    f"Login failed with status {response.status_code}",
                    status_code=response.status_code,
                    response_data=response_data,
                )

        except Exception as e:
            if isinstance(e, AuthenticationError):
                raise
            # Handle network errors specifically
            import httpx
            if isinstance(e, (httpx.ConnectError, httpx.TimeoutException)):
                from .exceptions import ConnectionError, TimeoutError
                if isinstance(e, httpx.ConnectError):
                    raise ConnectionError(f"Connection failed: {str(e)}", original_error=e)
                else:
                    raise TimeoutError(f"Request timed out: {str(e)}", timeout_duration=getattr(e, 'timeout', None))
            raise AuthenticationError(f"Login request failed: {str(e)}")

    async def _refresh_auth(self) -> None:
        """Refresh authentication token."""
        if not self._refresh_token:
            await self._perform_login()
            return

        if not self._http_client:
            raise AuthenticationError("Authentication not initialized - start session first")

        url = build_url(self.base_url, "auth", "refresh")
        headers = {"Authorization": f"Bearer {self._refresh_token}"}

        try:
            response = await self._http_client.post(url, headers=headers)

            if response.status_code == 200:
                token_data = response.json()
                self._store_tokens(token_data)
            elif response.status_code in (401, 403):
                # Refresh token expired or invalid, clear tokens and perform login
                self._clear_tokens()
                await self._perform_login()
            else:
                response_data = response.json() if response.content else None
                raise AuthenticationError(
                    f"Token refresh failed with status {response.status_code}",
                    status_code=response.status_code,
                    response_data=response_data,
                )

        except Exception as e:
            if isinstance(e, AuthenticationError):
                raise
            # If refresh fails, clear tokens and raise error instead of auto-login
            self._clear_tokens()
            raise AuthenticationError(f"Token refresh failed: {str(e)}")

    async def _revoke_token(self) -> None:
        """Revoke the current refresh token."""
        if not self._refresh_token or not self._http_client:
            return

        url = build_url(self.base_url, "auth", "refresh")
        headers = {"Authorization": f"Bearer {self._refresh_token}"}

        try:
            await self._http_client.delete(url, headers=headers)
        except Exception:
            # Ignore errors during token revocation
            pass

    def _store_tokens(self, token_data: Dict[str, Any]) -> None:
        """Store tokens from login/refresh response."""
        # Validate required fields
        if not token_data.get("access_token"):
            raise AuthenticationError("Malformed login response: missing access_token")
        
        self._access_token = token_data.get("access_token")
        self._refresh_token = token_data.get("refresh_token", self._refresh_token)

        # Calculate token expiry
        expires_in = token_data.get("expires_in")
        if expires_in:
            self._token_expires_at = datetime.now(UTC) + timedelta(seconds=expires_in)
        else:
            # Default to 1 hour if not specified
            self._token_expires_at = datetime.now(UTC) + timedelta(hours=1)

    def _clear_tokens(self) -> None:
        """Clear all stored tokens."""
        self._access_token = None
        self._refresh_token = None
        self._token_expires_at = None

    def get_current_user_info(self) -> Dict[str, Any]:
        """
        Get information about currently authenticated user.

        Returns:
            Dictionary with user information
        """
        if self.is_token_auth:
            return {
                "auth_type": "api_token",
                "authenticated": True,
            }
        else:
            return {
                "auth_type": "username_password",
                "username": self.username,
                "authenticated": self.is_authenticated,
                "token_expires_at": self._token_expires_at.isoformat() if self._token_expires_at else None,
                "needs_refresh": self.needs_refresh,
            }


class AuthenticationManager:
    """
    Higher-level authentication manager that can handle multiple auth methods.
    """

    def __init__(self) -> None:
        """Initialize authentication manager."""
        self._auth_handlers: Dict[str, MealieAuth] = {}
        self._default_handler: Optional[str] = None

    def add_auth(
        self,
        name: str,
        base_url: str,
        username: Optional[str] = None,
        password: Optional[str] = None,
        api_token: Optional[str] = None,
        **kwargs: Any,
    ) -> MealieAuth:
        """
        Add an authentication handler.

        Args:
            name: Name for this auth handler
            base_url: Base URL of the Mealie instance
            username: Username for authentication
            password: Password for authentication
            api_token: API token for authentication
            **kwargs: Additional arguments for MealieAuth

        Returns:
            Created MealieAuth instance
        """
        auth = MealieAuth(
            base_url=base_url,
            username=username,
            password=password,
            api_token=api_token,
            **kwargs,
        )

        self._auth_handlers[name] = auth

        # Set as default if it's the first one
        if self._default_handler is None:
            self._default_handler = name

        return auth

    def get_auth(self, name: Optional[str] = None) -> MealieAuth:
        """
        Get an authentication handler by name.

        Args:
            name: Name of the auth handler (uses default if None)

        Returns:
            MealieAuth instance

        Raises:
            ValueError: If handler not found
        """
        if name is None:
            name = self._default_handler

        if name is None or name not in self._auth_handlers:
            raise ValueError(f"Auth handler '{name}' not found")

        return self._auth_handlers[name]

    def set_default(self, name: str) -> None:
        """
        Set the default authentication handler.

        Args:
            name: Name of the auth handler to set as default

        Raises:
            ValueError: If handler not found
        """
        if name not in self._auth_handlers:
            raise ValueError(f"Auth handler '{name}' not found")

        self._default_handler = name

    def list_auth_handlers(self) -> List[str]:
        """
        List all available authentication handler names.

        Returns:
            List of handler names
        """
        return list(self._auth_handlers.keys())

    async def logout_all(self) -> None:
        """Logout from all authentication handlers."""
        for auth in self._auth_handlers.values():
            await auth.logout()


def create_auth_from_env(
    base_url: str,
    username_env: str = "MEALIE_USERNAME",
    password_env: str = "MEALIE_PASSWORD",
    token_env: str = "MEALIE_API_TOKEN",
    **kwargs: Any,
) -> MealieAuth:
    """
    Create authentication from environment variables.

    Args:
        base_url: Base URL of the Mealie instance
        username_env: Environment variable name for username
        password_env: Environment variable name for password
        token_env: Environment variable name for API token
        **kwargs: Additional arguments for MealieAuth

    Returns:
        Configured MealieAuth instance

    Raises:
        ConfigurationError: If no authentication method found in environment
    """
    import os

    api_token = os.getenv(token_env)
    username = os.getenv(username_env)
    password = os.getenv(password_env)

    if not api_token and not (username and password):
        raise ConfigurationError(
            f"No authentication found in environment. "
            f"Set either {token_env} or both {username_env} and {password_env}",
            config_field="environment_variables",
        )

    return MealieAuth(
        base_url=base_url,
        username=username,
        password=password,
        api_token=api_token,
        **kwargs,
    ) 