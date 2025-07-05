"""
E2E Testing Fixtures and Configuration

This module provides pytest fixtures for end-to-end testing
with real Mealie server instances.
"""

import asyncio
import pytest
from typing import AsyncGenerator, Dict, Any
from mealie_client import MealieClient

from .config import get_test_config, should_cleanup_data
from .base_test import AsyncBaseE2ETest
from .utils import E2ECleanup, E2EDataFactory


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def e2e_config():
    """Get E2E testing configuration."""
    config = get_test_config()
    config.validate()
    return config


@pytest.fixture(scope="session")
async def authenticated_client(e2e_config) -> AsyncGenerator[MealieClient, None]:
    """
    Create and authenticate a MealieClient for the test session.
    
    This fixture provides a shared client instance for all tests
    in the session to reduce authentication overhead.
    """
    client = MealieClient(
        base_url=e2e_config.base_url,
        timeout=e2e_config.timeout,
        max_retries=e2e_config.max_retries,
        retry_delay=e2e_config.retry_delay,
        **e2e_config.get_auth_kwargs()
    )
    
    try:
        await client.start_session()
        
        # Verify authentication works
        await client.health_check()
        
        yield client
        
    finally:
        await client.close_session()


@pytest.fixture
async def test_client(authenticated_client) -> AsyncGenerator[MealieClient, None]:
    """
    Provide a test client for individual test functions.
    
    This reuses the session client but ensures each test gets
    a clean state for resource tracking.
    """
    yield authenticated_client


@pytest.fixture
async def e2e_test_base(test_client) -> AsyncGenerator[AsyncBaseE2ETest, None]:
    """
    Create a base test instance for E2E testing.
    
    This fixture provides a configured base test instance
    with automatic setup and teardown.
    """
    test_instance = AsyncBaseE2ETest()
    test_instance.client = test_client
    test_instance.cleanup_manager = E2ECleanup(test_client)
    
    yield test_instance
    
    # Cleanup after test
    if should_cleanup_data():
        try:
            cleanup_results = await test_instance.cleanup_created_resources()
            if any(cleanup_results.values()):
                print(f"Cleaned up test resources: {cleanup_results}")
        except Exception as e:
            print(f"Error during resource cleanup: {e}")


@pytest.fixture
async def data_factory() -> E2EDataFactory:
    """Provide data factory for generating test data."""
    return E2EDataFactory()


@pytest.fixture
async def cleanup_manager(test_client) -> E2ECleanup:
    """Provide cleanup manager for manual resource cleanup."""
    return E2ECleanup(test_client)


# Test data fixtures
@pytest.fixture
def sample_recipe_data(data_factory) -> Dict[str, Any]:
    """Generate sample recipe data for testing."""
    return data_factory.generate_test_recipe_data()


@pytest.fixture
def sample_user_data(data_factory) -> Dict[str, Any]:
    """Generate sample user data for testing."""
    return data_factory.generate_test_user_data()


@pytest.fixture
def sample_group_data(data_factory) -> Dict[str, Any]:
    """Generate sample group data for testing."""
    return data_factory.generate_test_group_data()


@pytest.fixture
def sample_meal_plan_data(data_factory) -> Dict[str, Any]:
    """Generate sample meal plan data for testing."""
    return data_factory.generate_test_meal_plan_data()

@pytest.fixture
def sample_label_data(data_factory) -> Dict[str, Any]:
    """Generate sample label data for testing."""
    return data_factory.generate_test_label_data()


@pytest.fixture
def sample_shopping_list_data(data_factory) -> Dict[str, Any]:
    """Generate sample shopping list data for testing."""
    return data_factory.generate_test_shopping_list_data()

@pytest.fixture
def sample_food_data(data_factory) -> Dict[str, Any]:
    """Generate sample food data for testing."""
    return data_factory.generate_test_food_data()



@pytest.fixture
def sample_unit_data(data_factory) -> Dict[str, Any]:
    """Generate sample unit data for testing."""
    return data_factory.generate_test_unit_data()

@pytest.fixture
def sample_household_data(data_factory) -> Dict[str, Any]:
    """Generate sample household data for testing."""
    return data_factory.generate_test_household_data()


# Performance testing fixtures
@pytest.fixture
def skip_if_no_performance(e2e_config):
    """Skip test if performance testing is disabled."""
    if not e2e_config.run_performance_tests:
        pytest.skip("Performance testing is disabled")


@pytest.fixture
def skip_if_no_load_testing(e2e_config):
    """Skip test if load testing is disabled."""
    if not e2e_config.run_load_tests:
        pytest.skip("Load testing is disabled")


# Cleanup fixtures
@pytest.fixture(scope="session", autouse=True)
async def cleanup_before_tests(authenticated_client):
    """
    Clean up test data before running tests.
    
    This fixture runs automatically at the start of the test session
    to ensure a clean state.
    """
    if should_cleanup_data():
        cleanup_manager = E2ECleanup(authenticated_client)
        try:
            cleanup_results = await cleanup_manager.cleanup_all_test_data()
            if any(cleanup_results.values()):
                print(f"Pre-test cleanup completed: {cleanup_results}")
        except Exception as e:
            print(f"Warning: Pre-test cleanup failed: {e}")


@pytest.fixture(scope="session", autouse=True)
async def cleanup_after_tests(authenticated_client):
    """
    Clean up test data after all tests complete.
    
    This fixture runs automatically at the end of the test session
    to clean up any remaining test data.
    """
    yield  # Wait for all tests to complete
    
    if should_cleanup_data():
        cleanup_manager = E2ECleanup(authenticated_client)
        try:
            cleanup_results = await cleanup_manager.cleanup_all_test_data()
            if any(cleanup_results.values()):
                print(f"Post-test cleanup completed: {cleanup_results}")
        except Exception as e:
            print(f"Warning: Post-test cleanup failed: {e}")


# Utility fixtures for common test patterns
@pytest.fixture
async def created_recipe(e2e_test_base, sample_recipe_data):
    """Create a test recipe and track for cleanup."""
    recipe = await e2e_test_base.client.recipes.create(sample_recipe_data)
    e2e_test_base.track_created_resource('recipes', recipe.id)
    return recipe


@pytest.fixture
async def created_user(e2e_test_base, sample_user_data):
    """Create a test user and track for cleanup."""
    user = await e2e_test_base.client.users.create(sample_user_data)
    e2e_test_base.track_created_resource('users', user.id)
    return user


@pytest.fixture
async def created_group(e2e_test_base, sample_group_data):
    """
    Test group fixture - SKIPPED because Mealie API doesn't support group creation.
    
    Groups must be created manually via the Mealie web interface.
    Tests that depend on this fixture will be automatically skipped.
    """
    pytest.skip(
        "Group creation not supported via Mealie API. "
        "Groups must be created manually via web interface. "
        "Test skipped automatically."
    )


@pytest.fixture
async def created_meal_plan(e2e_test_base, sample_meal_plan_data):
    """Create a test meal plan and track for cleanup."""
    meal_plan = await e2e_test_base.client.meal_plans.create(sample_meal_plan_data)
    e2e_test_base.track_created_resource('meal_plans', meal_plan.id)
    return meal_plan


@pytest.fixture
async def created_shopping_list(e2e_test_base, sample_shopping_list_data):
    """Create a test shopping list and track for cleanup."""
    shopping_list = await e2e_test_base.client.shopping_lists.create(sample_shopping_list_data)
    e2e_test_base.track_created_resource('shopping_lists', shopping_list.id)
    return shopping_list

@pytest.fixture
async def created_food(e2e_test_base, sample_food_data):
    """Create a test food and track for cleanup."""
    food = await e2e_test_base.client.foods.create(sample_food_data)
    e2e_test_base.track_created_resource('foods', food.id)
    return food

@pytest.fixture
async def created_unit(e2e_test_base, sample_unit_data):
    """Create a test unit and track for cleanup."""
    unit = await e2e_test_base.client.units.create(sample_unit_data)
    e2e_test_base.track_created_resource('units', unit.id)
    return unit

@pytest.fixture
async def created_household(e2e_test_base, sample_household_data):
    """
    Test household fixture - SKIPPED because Mealie API doesn't support household creation.
    
    Households are read-only via API and must be created through the web interface.
    Tests that depend on this fixture will be automatically skipped.
    """
    pytest.skip(
        "Household creation not supported via Mealie API. "
        "Households are read-only via API. "
        "Test skipped automatically."
    )


# Parameterized fixtures for testing multiple scenarios
@pytest.fixture(params=[
    {"include_advanced_fields": True},
    {"include_advanced_fields": False}
])
def recipe_data_variants(request, data_factory):
    """Generate different variants of recipe data."""
    return data_factory.generate_test_recipe_data(**request.param)


@pytest.fixture(params=[
    {"admin": False},
    {"admin": True}
])
def user_data_variants(request, data_factory):
    """Generate different variants of user data."""
    return data_factory.generate_test_user_data(**request.param)


# Error simulation fixtures
@pytest.fixture
def invalid_recipe_data():
    """Generate invalid recipe data for error testing."""
    return {
        "name": "",  # Invalid: empty name
        "description": "This recipe has invalid data"
    }


@pytest.fixture
def invalid_user_data():
    """Generate invalid user data for error testing."""
    return {
        "username": "",  # Invalid: empty username
        "email": "invalid-email",  # Invalid: malformed email
        "password": "123"  # Invalid: too short
    } 