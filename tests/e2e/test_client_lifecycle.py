"""
E2E Client Lifecycle Tests

This module tests client lifecycle management including connection,
session management, context managers, and cleanup operations.
"""

import asyncio
import pytest
from typing import List
from mealie_client import MealieClient
from mealie_client.exceptions import AuthenticationError, ConnectionError, TimeoutError

from .config import get_test_config


class TestE2EClientLifecycle:
    """Test client lifecycle management in E2E environment."""
    
    @pytest.mark.asyncio
    async def test_basic_client_creation(self):
        """Test basic client creation and configuration."""
        config = get_test_config()
        config.validate()
        
        client = MealieClient(
            base_url=config.base_url,
            timeout=config.timeout,
            max_retries=config.max_retries,
            retry_delay=config.retry_delay,
            **config.get_auth_kwargs()
        )
        
        # Test initial state
        assert client.get_base_url() == config.base_url + "/api"
        assert not client.is_connected()
        
        # Test client info
        client_info = client.get_client_info()
        assert 'base_url' in client_info
        assert 'timeout' in client_info
        assert client_info['base_url'] == config.base_url + "/api"
    
    @pytest.mark.asyncio
    async def test_session_start_stop_cycle(self):
        """Test session start and stop cycle."""
        config = get_test_config()
        config.validate()
        
        client = MealieClient(
            base_url=config.base_url,
            timeout=config.timeout,
            **config.get_auth_kwargs()
        )
        
        # Initial state
        assert not client.is_connected()
        
        # Start session
        await client.start_session()
        assert client.is_connected()
        
        # Verify we can make requests
        health_response = await client.health_check()
        assert health_response is not None
        
        # Stop session
        await client.close_session()
        assert not client.is_connected()
        
        # Should auto-restart session on new requests
        health_response = await client.health_check()
        assert health_response is not None
        assert client.is_connected()  # Session should be restarted
        
        # Clean up
        await client.close_session()
    
    @pytest.mark.asyncio
    async def test_multiple_session_starts(self):
        """Test calling start_session multiple times."""
        config = get_test_config()
        config.validate()
        
        client = MealieClient(
            base_url=config.base_url,
            timeout=config.timeout,
            **config.get_auth_kwargs()
        )
        
        try:
            # Multiple calls to start_session should be safe
            await client.start_session()
            assert client.is_connected()
            
            await client.start_session()  # Second call
            assert client.is_connected()
            
            await client.start_session()  # Third call
            assert client.is_connected()
            
            # Should still be able to make requests
            health_response = await client.health_check()
            assert health_response is not None
            
        finally:
            await client.close_session()
    
    @pytest.mark.asyncio
    async def test_multiple_session_closes(self):
        """Test calling close_session multiple times."""
        config = get_test_config()
        config.validate()
        
        client = MealieClient(
            base_url=config.base_url,
            timeout=config.timeout,
            **config.get_auth_kwargs()
        )
        
        await client.start_session()
        assert client.is_connected()
        
        # Multiple calls to close_session should be safe
        await client.close_session()
        assert not client.is_connected()
        
        await client.close_session()  # Second call
        assert not client.is_connected()
        
        await client.close_session()  # Third call
        assert not client.is_connected()
    
    @pytest.mark.asyncio
    async def test_context_manager(self):
        """Test async context manager functionality."""
        config = get_test_config()
        config.validate()
        
        # Test successful context manager usage
        async with MealieClient(
            base_url=config.base_url,
            timeout=config.timeout,
            **config.get_auth_kwargs()
        ) as client:
            # Client should be automatically connected
            assert client.is_connected()
            
            # Should be able to make requests
            health_response = await client.health_check()
            assert health_response is not None
            
            app_info = await client.get_app_info()
            assert app_info is not None
        
        # Client should be automatically disconnected
        assert not client.is_connected()
    
    @pytest.mark.asyncio
    async def test_context_manager_with_exception(self):
        """Test context manager cleanup when exception occurs."""
        config = get_test_config()
        config.validate()
        
        client = None
        
        try:
            async with MealieClient(
                base_url=config.base_url,
                timeout=config.timeout,
                **config.get_auth_kwargs()
            ) as test_client:
                client = test_client
                assert client.is_connected()
                
                # Force an exception
                raise ValueError("Test exception")
                
        except ValueError:
            pass  # Expected exception
        
        # Client should still be properly closed
        assert client is not None
        assert not client.is_connected()
    
    @pytest.mark.asyncio
    async def test_nested_context_managers(self):
        """Test nested context manager usage."""
        config = get_test_config()
        config.validate()
        
        async with MealieClient(
            base_url=config.base_url,
            timeout=config.timeout,
            **config.get_auth_kwargs()
        ) as client1:
            assert client1.is_connected()
            
            async with MealieClient(
                base_url=config.base_url,
                timeout=config.timeout,
                **config.get_auth_kwargs()
            ) as client2:
                assert client2.is_connected()
                
                # Both clients should work
                health1 = await client1.health_check()
                health2 = await client2.health_check()
                
                assert health1 is not None
                assert health2 is not None
            
            # client2 should be closed, client1 still open
            assert not client2.is_connected()
            assert client1.is_connected()
            
            # client1 should still work
            health1 = await client1.health_check()
            assert health1 is not None
        
        # Both clients should be closed
        assert not client1.is_connected()
        assert not client2.is_connected()
    
    @pytest.mark.asyncio
    async def test_concurrent_clients(self):
        """Test multiple concurrent client instances."""
        config = get_test_config()
        config.validate()
        
        num_clients = 5
        clients: List[MealieClient] = []
        
        # Create multiple clients
        for i in range(num_clients):
            client = MealieClient(
                base_url=config.base_url,
                timeout=config.timeout,
                **config.get_auth_kwargs()
            )
            clients.append(client)
        
        try:
            # Start all sessions concurrently
            await asyncio.gather(*[client.start_session() for client in clients])
            
            # All should be connected
            for client in clients:
                assert client.is_connected()
            
            # Make concurrent requests
            health_responses = await asyncio.gather(*[
                client.health_check() for client in clients
            ])
            
            # All should succeed
            for response in health_responses:
                assert response is not None
            
            # Make concurrent app info requests
            app_info_responses = await asyncio.gather(*[
                client.get_app_info() for client in clients
            ])
            
            # All should succeed
            for response in app_info_responses:
                assert response is not None
        
        finally:
            # Close all clients
            await asyncio.gather(*[
                client.close_session() for client in clients
            ], return_exceptions=True)
            
            # All should be disconnected
            for client in clients:
                assert not client.is_connected()
    
    @pytest.mark.asyncio
    async def test_client_timeout_configuration(self):
        """Test client timeout configuration."""
        config = get_test_config()
        config.validate()
        
        # Test with very short timeout
        client = MealieClient(
            base_url=config.base_url,
            timeout=0.001,  # Very short timeout
            **config.get_auth_kwargs()
        )
        
        try:
            # This might timeout during session start or first request
            await client.start_session()
            
            # If we get here, try a request that might timeout
            with pytest.raises(TimeoutError):
                await client.health_check()
                
        except (TimeoutError, ConnectionError):
            # Expected - very short timeout should cause issues
            pass
        
        finally:
            await client.close_session()
    
    @pytest.mark.asyncio
    async def test_client_retry_configuration(self):
        """Test client retry configuration."""
        config = get_test_config()
        config.validate()
        
        client = MealieClient(
            base_url=config.base_url,
            timeout=config.timeout,
            max_retries=1,  # Minimal retries
            retry_delay=0.1,  # Short delay
            **config.get_auth_kwargs()
        )
        
        try:
            await client.start_session()
            assert client.is_connected()
            
            # Normal requests should work
            health_response = await client.health_check()
            assert health_response is not None
            
        finally:
            await client.close_session()
    
    @pytest.mark.asyncio
    async def test_connection_recovery(self):
        """Test connection recovery scenarios."""
        config = get_test_config()
        config.validate()
        
        client = MealieClient(
            base_url=config.base_url,
            timeout=config.timeout,
            **config.get_auth_kwargs()
        )
        
        try:
            await client.start_session()
            assert client.is_connected()
            
            # Make successful request
            health_response = await client.health_check()
            assert health_response is not None
            
            # Simulate connection interruption by closing and restarting
            await client.close_session()
            assert not client.is_connected()
            
            # Restart session
            await client.start_session()
            assert client.is_connected()
            
            # Should work again
            health_response = await client.health_check()
            assert health_response is not None
            
        finally:
            await client.close_session()


class TestE2EClientLifecycleIntegration:
    """Integration tests for client lifecycle with other operations."""
    
    @pytest.mark.asyncio
    async def test_client_lifecycle_with_data_operations(self, e2e_test_base):
        """Test client lifecycle doesn't interfere with data operations."""
        client = e2e_test_base.client
        
        # Test basic data operations work
        recipes = await client.recipes.get_all(per_page=5)
        assert isinstance(recipes, list)
        
        # Test client state during operations
        assert client.is_connected()
        
        # Test operations still work after multiple requests
        for i in range(3):
            health_response = await client.health_check()
            assert health_response is not None
            
            recipes = await client.recipes.get_all(per_page=2)
            assert isinstance(recipes, list)
    
    @pytest.mark.asyncio
    async def test_client_state_consistency(self, e2e_test_base):
        """Test client state remains consistent across operations."""
        client = e2e_test_base.client
        
        # Check initial state
        assert client.is_connected()
        
        # Perform various operations
        operations = [
            client.health_check(),
            client.get_app_info(),
            client.recipes.get_all(per_page=1),
        ]
        
        try:
            current_user = await client.users.get_current()
            operations.append(current_user)
        except Exception:
            pass  # User operations might not be available
        
        # Execute operations
        for operation in operations:
            if asyncio.iscoroutine(operation):
                result = await operation
                assert result is not None
        
        # Client should still be connected
        assert client.is_connected()
        
        # Auth info should still be valid
        auth_info = client.get_auth_info()
        assert auth_info['authenticated'] == True 