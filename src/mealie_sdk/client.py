"""
Main client for the Mealie SDK.

This module contains the primary MealieClient class that serves as the main
interface for interacting with the Mealie API.
"""

import asyncio
import json
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urljoin

from .auth import MealieAuth, create_auth_from_env
from .exceptions import (
    AuthenticationError,
    ConfigurationError,
    ConnectionError,
    MealieAPIError,
    TimeoutError,
    create_api_error_from_response,
)
from .utils import build_url, generate_request_id, normalize_base_url


class MealieClient:
    """
    Main client for interacting with the Mealie API.
    
    This class provides a high-level interface for all Mealie API operations,
    including recipes, meal planning, shopping lists, and user management.
    """

    def __init__(
        self,
        base_url: str,
        username: Optional[str] = None,
        password: Optional[str] = None,
        api_token: Optional[str] = None,
        timeout: float = 30.0,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        user_agent: Optional[str] = None,
        **auth_kwargs: Any,
    ) -> None:
        """
        Initialize the Mealie client.

        Args:
            base_url: Base URL of the Mealie instance (e.g., 'https://mealie.example.com')
            username: Username for authentication (alternative to api_token)
            password: Password for authentication (alternative to api_token)
            api_token: API token for authentication (alternative to username/password)
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries for failed requests
            retry_delay: Delay between retries in seconds
            user_agent: Custom User-Agent header
            **auth_kwargs: Additional arguments for authentication

        Raises:
            ConfigurationError: If configuration is invalid
        """
        # Normalize and validate the base URL
        self.base_url = normalize_base_url(base_url)
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        
        # Set up user agent
        if user_agent is None:
            user_agent = "mealie-sdk/0.1.0"
        self.user_agent = user_agent

        # Initialize authentication
        self.auth = MealieAuth(
            base_url=self.base_url,
            username=username,
            password=password,
            api_token=api_token,
            **auth_kwargs,
        )

        # HTTP client will be initialized on first use
        self._http_client: Optional[Any] = None
        self._session_started = False

        # API endpoint managers (will be initialized later)
        self.recipes: Optional[Any] = None
        self.users: Optional[Any] = None
        self.groups: Optional[Any] = None
        self.meal_plans: Optional[Any] = None
        self.shopping_lists: Optional[Any] = None

    @classmethod
    def from_env(cls, base_url: str, **kwargs: Any) -> "MealieClient":
        """
        Create a client using environment variables for authentication.

        Environment variables:
        - MEALIE_USERNAME: Username for authentication
        - MEALIE_PASSWORD: Password for authentication  
        - MEALIE_API_TOKEN: API token for authentication

        Args:
            base_url: Base URL of the Mealie instance
            **kwargs: Additional arguments for the client

        Returns:
            Configured MealieClient instance

        Raises:
            ConfigurationError: If no authentication found in environment
        """
        auth = create_auth_from_env(base_url)
        return cls(
            base_url=base_url,
            username=auth.username,
            password=auth.password,
            api_token=auth.api_token,
            **kwargs,
        )

    async def __aenter__(self) -> "MealieClient":
        """Async context manager entry."""
        await self.start_session()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        await self.close_session()

    async def start_session(self) -> None:
        """
        Start the HTTP session and initialize the client.
        
        This method must be called before making any API requests.
        """
        if self._session_started:
            return

        try:
            # Try to import httpx
            import httpx
        except ImportError:
            raise ConfigurationError(
                "httpx is required for HTTP requests. Install with: pip install httpx",
                config_field="dependencies",
            )

        # Create HTTP client
        self._http_client = httpx.AsyncClient(
            timeout=httpx.Timeout(self.timeout),
            headers={"User-Agent": self.user_agent},
        )

        # Set HTTP client on auth handler
        self.auth.set_http_client(self._http_client)

        # Initialize API endpoint managers
        await self._initialize_endpoints()

        # Perform initial authentication if using username/password
        if not self.auth.is_token_auth:
            await self.auth.login()

        self._session_started = True

    async def close_session(self) -> None:
        """Close the HTTP session and cleanup resources."""
        if not self._session_started:
            return

        if self._http_client:
            await self._http_client.aclose()
            self._http_client = None

        self._session_started = False

    async def _initialize_endpoints(self) -> None:
        """Initialize API endpoint managers."""
        # Import endpoint managers
        from .endpoints.recipes import RecipesManager
        from .endpoints.users import UsersManager
        from .endpoints.groups import GroupsManager
        from .endpoints.meal_plans import MealPlansManager
        from .endpoints.shopping_lists import ShoppingListsManager

        # Initialize endpoint managers
        self.recipes = RecipesManager(self)
        self.users = UsersManager(self)
        self.groups = GroupsManager(self)
        self.meal_plans = MealPlansManager(self)
        self.shopping_lists = ShoppingListsManager(self)

    async def request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        authenticated: bool = True,
        **kwargs: Any,
    ) -> Any:
        """
        Make an HTTP request to the Mealie API.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE, etc.)
            endpoint: API endpoint path (relative to base URL)
            params: Query parameters
            data: Form data
            json_data: JSON data for request body
            files: Files to upload
            headers: Additional headers
            authenticated: Whether authentication is required
            **kwargs: Additional arguments for the HTTP client

        Returns:
            Response data (parsed JSON if available)

        Raises:
            MealieAPIError: If the API returns an error
            ConnectionError: If connection fails
            TimeoutError: If request times out
        """
        if not self._session_started:
            await self.start_session()

        # Build the full URL
        url = build_url(self.base_url, endpoint, **(params or {}))

        # Prepare headers
        request_headers = headers.copy() if headers else {}
        
        # Add authentication headers if required
        if authenticated:
            auth_headers = await self.auth.get_auth_headers()
            request_headers.update(auth_headers)

        # Add request ID for tracking
        request_id = generate_request_id()
        request_headers["X-Request-ID"] = request_id

        # Prepare request arguments
        request_kwargs = {
            "method": method.upper(),
            "url": url,
            "headers": request_headers,
            **kwargs,
        }

        if json_data is not None:
            request_kwargs["json"] = json_data
        elif data is not None:
            request_kwargs["data"] = data

        if files is not None:
            request_kwargs["files"] = files

        # Make the request with retries
        last_exception = None
        for attempt in range(self.max_retries + 1):
            try:
                response = await self._http_client.request(**request_kwargs)
                return await self._handle_response(response, request_id)

            except Exception as e:
                last_exception = e
                
                # Don't retry on authentication/authorization errors
                if isinstance(e, (AuthenticationError, AuthorizationError)):
                    raise

                # Don't retry on the last attempt
                if attempt == self.max_retries:
                    break

                # Wait before retrying
                await asyncio.sleep(self.retry_delay * (2 ** attempt))

        # Handle final failure
        if isinstance(last_exception, MealieAPIError):
            raise last_exception
        else:
            raise ConnectionError(
                f"Request failed after {self.max_retries + 1} attempts",
                original_error=last_exception,
            )

    async def _handle_response(self, response: Any, request_id: str) -> Any:
        """
        Handle HTTP response and extract data or raise appropriate errors.

        Args:
            response: HTTP response object
            request_id: Request ID for tracking

        Returns:
            Parsed response data

        Raises:
            MealieAPIError: If the response indicates an error
        """
        # Handle successful responses
        if 200 <= response.status_code < 300:
            # Try to parse JSON response
            if response.headers.get("content-type", "").startswith("application/json"):
                try:
                    return response.json()
                except (json.JSONDecodeError, ValueError):
                    # If JSON parsing fails, return raw content
                    return response.content

            # For non-JSON responses, return content
            return response.content

        # Handle error responses
        response_data = None
        if response.headers.get("content-type", "").startswith("application/json"):
            try:
                response_data = response.json()
            except (json.JSONDecodeError, ValueError):
                pass

        # Create and raise appropriate error
        error = create_api_error_from_response(
            status_code=response.status_code,
            response_data=response_data,
            request_id=request_id,
        )
        raise error

    # Convenience methods for common HTTP operations

    async def get(self, endpoint: str, **kwargs: Any) -> Any:
        """Make a GET request."""
        return await self.request("GET", endpoint, **kwargs)

    async def post(self, endpoint: str, **kwargs: Any) -> Any:
        """Make a POST request."""
        return await self.request("POST", endpoint, **kwargs)

    async def put(self, endpoint: str, **kwargs: Any) -> Any:
        """Make a PUT request."""
        return await self.request("PUT", endpoint, **kwargs)

    async def patch(self, endpoint: str, **kwargs: Any) -> Any:
        """Make a PATCH request."""
        return await self.request("PATCH", endpoint, **kwargs)

    async def delete(self, endpoint: str, **kwargs: Any) -> Any:
        """Make a DELETE request."""
        return await self.request("DELETE", endpoint, **kwargs)

    # Health and information methods

    async def health_check(self) -> Dict[str, Any]:
        """
        Check the health status of the Mealie instance.

        Returns:
            Health check information
        """
        return await self.get("app/about", authenticated=False)

    async def get_app_info(self) -> Dict[str, Any]:
        """
        Get application information about the Mealie instance.

        Returns:
            Application information including version, build info, etc.
        """
        return await self.get("app/about", authenticated=False)

    async def get_app_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the Mealie instance.

        Returns:
            Statistics including recipe count, user count, etc.
        """
        return await self.get("app/statistics")

    # Authentication methods

    async def login(self) -> None:
        """
        Perform login (only needed for username/password authentication).
        
        For API token authentication, this is a no-op.
        """
        await self.auth.login()

    async def logout(self) -> None:
        """Logout and clear authentication state."""
        await self.auth.logout()

    async def refresh_token(self) -> None:
        """Refresh the authentication token (only for username/password auth)."""
        await self.auth.refresh_token()

    def get_auth_info(self) -> Dict[str, Any]:
        """
        Get information about the current authentication state.

        Returns:
            Authentication information
        """
        return self.auth.get_current_user_info()

    # Utility methods

    def is_connected(self) -> bool:
        """Check if the client is connected and ready for requests."""
        return self._session_started and self._http_client is not None

    def get_base_url(self) -> str:
        """Get the base URL of the Mealie instance."""
        return self.base_url

    def get_client_info(self) -> Dict[str, Any]:
        """
        Get information about the client configuration.

        Returns:
            Client configuration information
        """
        return {
            "base_url": self.base_url,
            "timeout": self.timeout,
            "max_retries": self.max_retries,
            "retry_delay": self.retry_delay,
            "user_agent": self.user_agent,
            "connected": self.is_connected(),
            "auth_info": self.get_auth_info(),
        } 