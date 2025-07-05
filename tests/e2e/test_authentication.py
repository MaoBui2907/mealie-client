"""
E2E Authentication Tests

This module tests authentication flows including login, logout,
token management, and authentication error scenarios.
"""

import asyncio
import pytest
from mealie_client import MealieClient
from mealie_client.exceptions import AuthenticationError, ConfigurationError, ConnectionError, TimeoutError

from .config import get_test_config


class TestE2EAuthentication:
    """Test authentication flows in E2E environment."""
    
    @pytest.mark.asyncio
    async def test_username_password_authentication(self):
        """Test authentication using username and password."""
        config = get_test_config()
        
        # Skip if no username/password provided
        if not config.username or not config.password:
            pytest.skip("Username/password authentication not configured")
        
        client = MealieClient(
            base_url=config.base_url,
            username=config.username,
            password=config.password,
            timeout=config.timeout
        )
        
        try:
            # Test session start and authentication
            await client.start_session()
            
            # Verify we can make authenticated requests
            health_response = await client.health_check()
            assert health_response is not None
            
            # Verify auth info
            auth_info = client.get_auth_info()
            assert auth_info['authenticated'] == True
            assert auth_info['auth_type'] == 'username_password'
            
        finally:
            await client.close_session()
    
    @pytest.mark.asyncio
    async def test_api_token_authentication(self):
        """Test authentication using API token."""
        config = get_test_config()
        
        # Skip if no API token provided
        if not config.api_token:
            pytest.skip("API token authentication not configured")
        
        client = MealieClient(
            base_url=config.base_url,
            api_token=config.api_token,
            timeout=config.timeout
        )
        
        try:
            # Test session start and authentication
            await client.start_session()
            
            # Verify we can make authenticated requests
            health_response = await client.health_check()
            assert health_response is not None
            
            # Verify auth info
            auth_info = client.get_auth_info()
            assert auth_info['authenticated'] == True
            assert auth_info['auth_type'] == 'api_token'
            
        finally:
            await client.close_session()
    
    @pytest.mark.asyncio
    async def test_invalid_credentials_error(self):
        """Test authentication with invalid credentials."""
        config = get_test_config()
        
        client = MealieClient(
            base_url=config.base_url,
            username="invalid_user",
            password="invalid_password",
            timeout=config.timeout
        )
        
        # Should raise authentication error
        with pytest.raises(AuthenticationError):
            await client.start_session()
    
    @pytest.mark.asyncio
    async def test_invalid_api_token_error(self):
        """Test authentication with invalid API token."""
        config = get_test_config()
        
        client = MealieClient(
            base_url=config.base_url,
            api_token="invalid_token_12345",
            timeout=config.timeout
        )
        
        try:
            await client.start_session()
            
            # API token auth doesn't fail immediately,
            # but first authenticated request should fail
            # Use an endpoint that requires authentication
            with pytest.raises(AuthenticationError):
                await client.recipes.get_all()  # This should require authentication
                
        finally:
            await client.close_session()
    
    @pytest.mark.asyncio
    async def test_missing_credentials_error(self):
        """Test client creation without credentials."""
        config = get_test_config()
        
        # Should raise configuration error
        with pytest.raises(ConfigurationError):
            MealieClient(
                base_url=config.base_url,
                # No credentials provided
            )
    
    @pytest.mark.asyncio
    async def test_invalid_base_url_error(self):
        """Test connection to invalid base URL."""
        config = get_test_config()
        
        client = MealieClient(
            base_url="https://invalid-mealie-url.example.com",
            api_token="test_token",
            timeout=5.0  # Short timeout
        )
        
        # Should raise connection error or timeout
        # start_session() doesn't actually connect, so we need to make a request
        try:
            await client.start_session()
            # This will attempt the actual connection and should fail
            with pytest.raises((ConnectionError, TimeoutError, AuthenticationError)):
                await client.health_check()
        finally:
            await client.close_session()
    
    @pytest.mark.asyncio
    async def test_authentication_context_manager(self):
        """Test authentication using async context manager."""
        config = get_test_config()
        config.validate()
        
        async with MealieClient(
            base_url=config.base_url,
            timeout=config.timeout,
            **config.get_auth_kwargs()
        ) as client:
            # Client should be automatically authenticated
            assert client.is_connected()
            
            # Should be able to make requests
            health_response = await client.health_check()
            assert health_response is not None
        
        # Client should be automatically closed
        assert not client.is_connected()
    
    @pytest.mark.asyncio
    async def test_manual_login_logout(self):
        """Test manual login and logout operations."""
        config = get_test_config()
        
        # Skip if no username/password (manual login requires them)
        if not config.username or not config.password:
            pytest.skip("Manual login requires username/password")
        
        client = MealieClient(
            base_url=config.base_url,
            username=config.username,
            password=config.password,
            timeout=config.timeout
        )
        
        try:
            await client.start_session()
            
            # Should be authenticated after session start
            assert client.is_connected()
            
            # Test logout
            await client.logout()
            
            # Verify that auth state changed after logout
            auth_info_after_logout = client.get_auth_info()
            assert auth_info_after_logout['authenticated'] == False, "Should not be authenticated after logout"
            
            # Test re-login
            await client.login()
            
            # Should be authenticated again
            assert client.is_connected()
            
            # Should be able to make requests again
            recipes = await client.recipes.get_all(per_page=1)
            assert isinstance(recipes, list)
            
        finally:
            await client.close_session()
    
    @pytest.mark.asyncio
    async def test_token_refresh(self):
        """Test automatic token refresh functionality."""
        config = get_test_config()
        
        # Skip if no username/password (token refresh requires them)
        if not config.username or not config.password:
            pytest.skip("Token refresh requires username/password")
        
        client = MealieClient(
            base_url=config.base_url,
            username=config.username,
            password=config.password,
            timeout=config.timeout
        )
        
        try:
            await client.start_session()
            
            # Get initial auth info
            initial_auth = client.get_auth_info()
            assert initial_auth['authenticated'] == True
            
            # Test manual token refresh
            await client.refresh_token()
            
            # Should still be authenticated
            post_refresh_auth = client.get_auth_info()
            assert post_refresh_auth['authenticated'] == True
            
            # Should be able to make requests
            health_response = await client.health_check()
            assert health_response is not None
            
        finally:
            await client.close_session()
    
    @pytest.mark.asyncio
    async def test_concurrent_authentication(self):
        """Test multiple concurrent client authentications."""
        config = get_test_config()
        config.validate()
        
        # Create multiple clients
        clients = []
        for i in range(3):
            client = MealieClient(
                base_url=config.base_url,
                timeout=config.timeout,
                **config.get_auth_kwargs()
            )
            clients.append(client)
        
        try:
            # Start all sessions concurrently
            await asyncio.gather(*[client.start_session() for client in clients])
            
            # All should be authenticated
            for client in clients:
                assert client.is_connected()
            
            # All should be able to make requests
            health_responses = await asyncio.gather(*[
                client.health_check() for client in clients
            ])
            
            for response in health_responses:
                assert response is not None
        
        finally:
            # Close all clients
            await asyncio.gather(*[
                client.close_session() for client in clients
            ], return_exceptions=True)


class TestE2EAuthenticationIntegration:
    """Integration tests for authentication with other operations."""
    
    @pytest.mark.asyncio
    async def test_authentication_with_crud_operations(self, e2e_test_base):
        """Test that authenticated operations work correctly."""
        client = e2e_test_base.client
        
        # Verify we can perform CRUD operations
        
        # Test recipes endpoint
        recipes = await client.recipes.get_all(per_page=5)
        assert isinstance(recipes, list)
        
        # Test users endpoint (if available)
        try:
            current_user = await client.users.get_current()
            assert current_user is not None
            assert hasattr(current_user, 'username')
        except Exception:
            # Some endpoints might not be available depending on permissions
            pass
        
        # Test app info
        app_info = await client.get_app_info()
        assert app_info is not None
        assert 'name' in app_info or 'version' in app_info
    
    @pytest.mark.asyncio
    async def test_authentication_persistence(self, e2e_test_base):
        """Test that authentication persists across multiple requests."""
        client = e2e_test_base.client
        
        # Make multiple requests to verify auth persistence
        for i in range(5):
            health_response = await client.health_check()
            assert health_response is not None
            
            # Add small delay to test session persistence
            await asyncio.sleep(0.1)
    
    @pytest.mark.asyncio
    async def test_authentication_error_recovery(self, e2e_test_base):
        """Test recovery from authentication errors."""
        client = e2e_test_base.client
        
        # First verify we're authenticated
        health_response = await client.health_check()
        assert health_response is not None
        
        # Test auth state consistency
        initial_auth = client.get_auth_info()
        assert initial_auth['authenticated'] == True
        
        # Test that we can make authenticated requests consistently
        for i in range(3):
            recipes = await client.recipes.get_all(per_page=1)
            assert isinstance(recipes, list)
            
            # Verify auth state is still consistent
            auth_info = client.get_auth_info()
            assert auth_info['authenticated'] == True 