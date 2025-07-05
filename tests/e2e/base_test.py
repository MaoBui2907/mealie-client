"""
Base E2E Test Class

This module provides a base test class for end-to-end testing
with common setup, teardown, and utility methods.
"""

import asyncio
import pytest
from typing import List, Optional, Dict, Any
from mealie_client import MealieClient
from mealie_client.exceptions import AuthenticationError

from .config import get_test_config, should_cleanup_data
from .utils import E2ECleanup, E2EDataFactory


class BaseE2ETest:
    """
    Base class for end-to-end tests.
    
    Provides common setup, teardown, and utility methods for E2E testing.
    """
    
    def __init__(self):
        """Initialize base test."""
        self.config = get_test_config()
        self.client: Optional[MealieClient] = None
        self.cleanup_manager: Optional[E2ECleanup] = None
        self.created_resources: Dict[str, List[str]] = {
            'recipes': [],
            'users': [],
            'groups': [],
            'meal_plans': [],
            'shopping_lists': []
        }
    
    async def setup_client(self) -> MealieClient:
        """
        Set up and authenticate the test client.
        
        Returns:
            Authenticated MealieClient instance
        """
        if self.client is not None:
            return self.client
        
        # Validate configuration
        self.config.validate()
        
        # Create client
        self.client = MealieClient(
            base_url=self.config.base_url,
            timeout=self.config.timeout,
            max_retries=self.config.max_retries,
            retry_delay=self.config.retry_delay,
            **self.config.get_auth_kwargs()
        )
        
        # Start session and authenticate
        try:
            await self.client.start_session()
            
            # Verify authentication works
            await self.verify_authentication()
            
        except Exception as e:
            await self.teardown_client()
            raise AuthenticationError(f"Failed to authenticate with Mealie server: {e}")
        
        # Initialize cleanup manager
        self.cleanup_manager = E2ECleanup(self.client)
        
        return self.client
    
    async def teardown_client(self) -> None:
        """Clean up the test client."""
        if self.client:
            try:
                await self.client.close_session()
            except Exception:
                pass  # Ignore errors during cleanup
            finally:
                self.client = None
                self.cleanup_manager = None
    
    async def verify_authentication(self) -> None:
        """Verify that authentication is working."""
        if not self.client:
            raise RuntimeError("Client not initialized")
        
        # Try a simple API call that requires authentication
        try:
            await self.client.health_check()
        except Exception as e:
            raise AuthenticationError(f"Authentication verification failed: {e}")
    
    async def cleanup_created_resources(self) -> Dict[str, int]:
        """
        Clean up resources created during the test.
        
        Returns:
            Dictionary with cleanup counts for each resource type
        """
        if not self.cleanup_manager:
            return {}
        
        return await self.cleanup_manager.cleanup_specific_resources(
            recipe_ids=self.created_resources.get('recipes'),
            user_ids=self.created_resources.get('users'),
            group_ids=self.created_resources.get('groups'),
            meal_plan_ids=self.created_resources.get('meal_plans'),
            shopping_list_ids=self.created_resources.get('shopping_lists')
        )
    
    async def cleanup_all_test_data(self) -> Dict[str, int]:
        """
        Clean up all test data (not just created in this test).
        
        Returns:
            Dictionary with cleanup counts for each resource type
        """
        if not self.cleanup_manager:
            return {}
        
        return await self.cleanup_manager.cleanup_all_test_data()
    
    def track_created_resource(self, resource_type: str, resource_id: str) -> None:
        """
        Track a created resource for cleanup.
        
        Args:
            resource_type: Type of resource (recipes, users, etc.)
            resource_id: ID of the created resource
        """
        if resource_type in self.created_resources:
            self.created_resources[resource_type].append(resource_id)
    
    async def create_test_recipe(self, **kwargs) -> 'Recipe':
        """
        Create a test recipe and track it for cleanup.
        
        Args:
            **kwargs: Override data for recipe creation
            
        Returns:
            Created Recipe object
        """
        if not self.client or not self.client.recipes:
            raise RuntimeError("Client not initialized")
        
        recipe_data = E2EDataFactory.generate_test_recipe_data(**kwargs)
        recipe = await self.client.recipes.create(recipe_data)
        
        # Track for cleanup
        self.track_created_resource('recipes', recipe.id)
        
        return recipe
    
    async def create_test_user(self, **kwargs) -> 'User':
        """
        Create a test user and track it for cleanup.
        
        Args:
            **kwargs: Override data for user creation
            
        Returns:
            Created User object
        """
        if not self.client or not self.client.users:
            raise RuntimeError("Client not initialized")
        
        user_data = E2EDataFactory.generate_test_user_data(**kwargs)
        user = await self.client.users.create(user_data)
        
        # Track for cleanup
        self.track_created_resource('users', user.id)
        
        return user
    
    async def create_test_group(self, **kwargs) -> 'Group':
        """
        Create a test group and track it for cleanup.
        
        Note: Group creation is not supported via Mealie API.
        This method will skip any test that calls it.
        
        Args:
            **kwargs: Override data for group creation
            
        Returns:
            This method never returns - always skips
        """
        pytest.skip(
            "Group creation not supported via Mealie API. "
            "Groups must be created manually via web interface. "
            "Test skipped automatically."
        )
    
    async def create_test_meal_plan(self, **kwargs) -> 'MealPlan':
        """
        Create a test meal plan and track it for cleanup.
        
        Args:
            **kwargs: Override data for meal plan creation
            
        Returns:
            Created MealPlan object
        """
        if not self.client or not self.client.meal_plans:
            raise RuntimeError("Client not initialized")
        
        meal_plan_data = E2EDataFactory.generate_test_meal_plan_data(**kwargs)
        meal_plan = await self.client.meal_plans.create(meal_plan_data)
        
        # Track for cleanup
        self.track_created_resource('meal_plans', meal_plan.id)
        
        return meal_plan
    
    async def create_test_shopping_list(self, **kwargs) -> 'ShoppingList':
        """
        Create a test shopping list and track it for cleanup.
        
        Args:
            **kwargs: Override data for shopping list creation
            
        Returns:
            Created ShoppingList object
        """
        if not self.client or not self.client.shopping_lists:
            raise RuntimeError("Client not initialized")
        
        shopping_list_data = E2EDataFactory.generate_test_shopping_list_data(**kwargs)
        shopping_list = await self.client.shopping_lists.create(shopping_list_data)
        
        # Track for cleanup
        self.track_created_resource('shopping_lists', shopping_list.id)
        
        return shopping_list
    
    async def wait_for_resource(
        self,
        resource_id: str,
        get_func,
        max_attempts: int = 5,
        delay: float = 1.0
    ) -> Any:
        """
        Wait for a resource to be available (eventually consistent).
        
        Args:
            resource_id: ID of the resource to wait for
            get_func: Function to get the resource
            max_attempts: Maximum number of attempts
            delay: Delay between attempts in seconds
            
        Returns:
            The resource object
        """
        for attempt in range(max_attempts):
            try:
                return await get_func(resource_id)
            except Exception:
                if attempt < max_attempts - 1:
                    await asyncio.sleep(delay)
                else:
                    raise
    
    def skip_if_not_supported(self, feature: str) -> None:
        """
        Skip test if a feature is not supported.
        
        Args:
            feature: Name of the feature to check
        """
        # This can be extended to check server capabilities
        pass
    
    def skip_if_performance_disabled(self) -> None:
        """Skip test if performance testing is disabled."""
        if not self.config.run_performance_tests:
            pytest.skip("Performance testing is disabled")
    
    def skip_if_load_testing_disabled(self) -> None:
        """Skip test if load testing is disabled."""
        if not self.config.run_load_tests:
            pytest.skip("Load testing is disabled")


class AsyncBaseE2ETest(BaseE2ETest):
    """
    Async version of BaseE2ETest for pytest-asyncio.
    
    This class provides async setup and teardown methods for use with pytest fixtures.
    """
    
    async def async_setup(self) -> None:
        """Async setup method for pytest fixtures."""
        await self.setup_client()
    
    async def async_teardown(self) -> None:
        """Async teardown method for pytest fixtures."""
        # Cleanup created resources if enabled
        if should_cleanup_data():
            try:
                cleanup_results = await self.cleanup_created_resources()
                if any(cleanup_results.values()):
                    print(f"Cleaned up test resources: {cleanup_results}")
            except Exception as e:
                print(f"Error during resource cleanup: {e}")
        
        # Close client
        await self.teardown_client()


# Utility functions for test methods
def requires_client(func):
    """Decorator to ensure client is initialized."""
    async def wrapper(self, *args, **kwargs):
        if not self.client:
            await self.setup_client()
        return await func(self, *args, **kwargs)
    return wrapper


def tracks_resource(resource_type: str):
    """Decorator to automatically track created resources."""
    def decorator(func):
        async def wrapper(self, *args, **kwargs):
            result = await func(self, *args, **kwargs)
            if hasattr(result, 'id') and result.id:
                self.track_created_resource(resource_type, result.id)
            return result
        return wrapper
    return decorator 