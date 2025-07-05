"""
Shared pytest fixtures and configuration for the Mealie SDK test suite.

This module provides common fixtures for HTTP mocking, test data factories,
and other utilities used across unit and integration tests.
"""

import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest
import httpx
import respx

from mealie_client import MealieClient, MealieAuth
from mealie_client.models import (
    Recipe, RecipeCreateRequest, RecipeSummary,
    User, UserCreateRequest, UserSummary,
    Group, GroupSummary,
    MealPlan, ShoppingList,
    UserRole, RecipeVisibility,
    Unit, UnitCreateRequest, UnitSummary,
    Food, FoodCreateRequest, FoodSummary,
    Household, HouseholdSummary
)


# Configure pytest for async testing
pytest_plugins = ('pytest_asyncio',)


# Test Configuration
TEST_BASE_URL = "https://test.mealie.com"
TEST_USERNAME = "test_user"
TEST_PASSWORD = "test_password"
TEST_API_TOKEN = "test_api_token_12345"
TEST_USER_ID = "user_123"
TEST_GROUP_ID = "group_456"


@pytest.fixture
def base_url() -> str:
    """Base URL for test API requests."""
    return TEST_BASE_URL


@pytest.fixture
def test_credentials() -> Dict[str, str]:
    """Test authentication credentials."""
    return {
        "username": TEST_USERNAME,
        "password": TEST_PASSWORD,
        "api_token": TEST_API_TOKEN
    }


@pytest.fixture
def mock_env_vars(monkeypatch):
    """Mock environment variables for testing."""
    monkeypatch.setenv("MEALIE_USERNAME", TEST_USERNAME)
    monkeypatch.setenv("MEALIE_PASSWORD", TEST_PASSWORD)
    monkeypatch.setenv("MEALIE_API_TOKEN", TEST_API_TOKEN)


@pytest.fixture
def httpx_mock():
    """HTTP mock for intercepting API requests."""
    with respx.mock as mock:
        yield mock


@pytest.fixture
async def mock_http_client():
    """Mock HTTP client for testing."""
    client = AsyncMock(spec=httpx.AsyncClient)
    client.aclose = AsyncMock()
    return client


@pytest.fixture
def auth_token_response() -> Dict[str, Any]:
    """Mock authentication token response."""
    return {
        "access_token": "mock_access_token_12345",
        "refresh_token": "mock_refresh_token_67890", 
        "token_type": "bearer",
        "expires_in": 3600,
        "expires_at": (datetime.utcnow() + timedelta(hours=1)).isoformat()
    }


@pytest.fixture
async def mealie_auth(base_url: str, test_credentials: Dict[str, str]) -> MealieAuth:
    """Create a MealieAuth instance for testing."""
    return MealieAuth(
        base_url=base_url,
        username=test_credentials["username"],
        password=test_credentials["password"]
    )


@pytest.fixture
async def mealie_auth_token(base_url: str, test_credentials: Dict[str, str]) -> MealieAuth:
    """Create a MealieAuth instance with API token for testing."""
    return MealieAuth(
        base_url=base_url,
        api_token=test_credentials["api_token"]
    )


@pytest.fixture
async def mealie_client(base_url: str, test_credentials: Dict[str, str]) -> MealieClient:
    """Create a MealieClient instance for testing."""
    return MealieClient(
        base_url=base_url,
        username=test_credentials["username"],
        password=test_credentials["password"]
    )


@pytest.fixture
async def mealie_client_token(base_url: str, test_credentials: Dict[str, str]) -> MealieClient:
    """Create a MealieClient instance with API token for testing."""
    return MealieClient(
        base_url=base_url,
        api_token=test_credentials["api_token"]
    )


# Test Data Factory Functions

def create_test_user_data(**kwargs) -> Dict[str, Any]:
    """Create test user data."""
    defaults = {
        "id": str(uuid4()),
        "username": f"user_{uuid4().hex[:8]}",
        "email": f"test_{uuid4().hex[:8]}@example.com",
        "full_name": "Test User",
        "admin": False,
        "group": TEST_GROUP_ID,
        "advanced": False,
        "can_invite": False,
        "can_manage": False,
        "can_organize": False,
        "login_attemps": 0,
        "locked_at": None,
        "date_updated": datetime.utcnow().isoformat(),
        "cache_key": str(uuid4())
    }
    defaults.update(kwargs)
    return defaults


def create_test_user(**kwargs) -> User:
    """Create a test User instance."""
    data = create_test_user_data(**kwargs)
    return User.from_dict(data)


def create_test_user_create_request(**kwargs) -> UserCreateRequest:
    """Create a test UserCreateRequest instance."""
    defaults = {
        "username": f"newuser_{uuid4().hex[:8]}",
        "email": f"newuser_{uuid4().hex[:8]}@example.com",
        "full_name": "New Test User",
        "password": "test_password_123",
        "admin": False
    }
    defaults.update(kwargs)
    return UserCreateRequest(**defaults)


def create_test_recipe_data(**kwargs) -> Dict[str, Any]:
    """Create test recipe data."""
    defaults = {
        "id": str(uuid4()),
        "user_id": TEST_USER_ID,
        "group_id": TEST_GROUP_ID,
        "name": f"Test Recipe {uuid4().hex[:8]}",
        "slug": f"test-recipe-{uuid4().hex[:8]}",
        "image": "test-recipe.jpg",
        "description": "A delicious test recipe",
        "recipe_yield": "4 servings",
        "recipe_ingredient": [
            {
                "title": "Main Ingredients",
                "note": "Fresh ingredients preferred",
                "unit": {"name": "cup"},
                "food": {"name": "flour"},
                "quantity": 2.0,
                "original_text": "2 cups flour"
            }
        ],
        "recipe_instructions": [
            {
                "id": str(uuid4()),
                "position": 1,
                "type": "step",
                "title": "Preparation",
                "text": "Mix all ingredients together."
            }
        ],
        "prep_time": "PT15M",
        "cook_time": "PT30M",
        "total_time": "PT45M",
        "recipe_category": [{"name": "Main Course", "slug": "main-course"}],
        "tags": [{"name": "Easy", "slug": "easy"}],
        "tools": [{"name": "Mixing Bowl", "slug": "mixing-bowl"}],
        "rating": 4.5,
        "date_added": datetime.utcnow().isoformat(),
        "date_updated": datetime.utcnow().isoformat()
    }
    defaults.update(kwargs)
    return defaults


def create_test_recipe(**kwargs) -> Recipe:
    """Create a test Recipe instance."""
    data = create_test_recipe_data(**kwargs)
    return Recipe.from_dict(data)


def create_test_recipe_create_request(**kwargs) -> RecipeCreateRequest:
    """Create a test RecipeCreateRequest instance."""
    defaults = {
        "name": f"New Recipe {uuid4().hex[:8]}",
        "description": "A new test recipe"
    }
    defaults.update(kwargs)
    return RecipeCreateRequest(**defaults)


def create_test_group_data(**kwargs) -> Dict[str, Any]:
    """Create test group data."""
    defaults = {
        "id": str(uuid4()),
        "name": f"Test Group {uuid4().hex[:8]}",
        "slug": f"test-group-{uuid4().hex[:8]}", 
        "webhook_urls": [],
        "webhook_time": "00:00",
        "webhook_enable": False,
        "categories": [],
        "tags": [],
        "tools": [],
        "users": [],
        "preferences": {}
    }
    defaults.update(kwargs)
    return defaults


def create_test_shopping_list_data(**kwargs) -> Dict[str, Any]:
    """Create test shopping list data."""
    defaults = {
        "id": str(uuid4()),
        "group_id": TEST_GROUP_ID,
        "user_id": TEST_USER_ID,
        "name": f"Test Shopping List {uuid4().hex[:8]}",
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
        "list_items": []
    }
    defaults.update(kwargs)
    return defaults


def create_test_meal_plan_data(**kwargs) -> Dict[str, Any]:
    """Create test meal plan data."""
    defaults = {
        "id": str(uuid4()),
        "group_id": TEST_GROUP_ID,
        "user_id": TEST_USER_ID,
        "start_date": datetime.utcnow().date().isoformat(),
        "end_date": (datetime.utcnow().date() + timedelta(days=6)).isoformat(),
        "plan_rules": [],
        "shopping_list": None
    }
    defaults.update(kwargs)
    return defaults


# Mock Response Fixtures

@pytest.fixture
def mock_health_response() -> Dict[str, Any]:
    """Mock health check response."""
    return {
        "status": "ok",
        "message": "Mealie is running!",
        "version": "1.0.0"
    }


@pytest.fixture  
def mock_app_info_response() -> Dict[str, Any]:
    """Mock app info response."""
    return {
        "production": False,
        "version": "1.0.0",
        "demo_status": False,
        "allow_signup": True,
        "build_id": "dev"
    }


@pytest.fixture
def mock_recipes_list_response() -> Dict[str, Any]:
    """Mock recipes list response."""
    recipes = [create_test_recipe_data() for _ in range(3)]
    return {
        "page": 1,
        "per_page": 50,
        "total": 3,
        "total_pages": 1,
        "items": recipes
    }


@pytest.fixture
def mock_users_list_response() -> Dict[str, Any]:
    """Mock users list response."""
    users = [create_test_user_data() for _ in range(2)]
    return {
        "page": 1,
        "per_page": 50,
        "total": 2,
        "total_pages": 1,
        "items": users
    }


# Utility Functions for Tests

def assert_called_with_auth_headers(mock_request, expected_token: Optional[str] = None):
    """Assert that a request was called with proper authentication headers."""
    call_args = mock_request.call_args
    if call_args and len(call_args) > 1:
        headers = call_args[1].get("headers", {})
        if expected_token:
            assert headers.get("Authorization") == f"Bearer {expected_token}"
        else:
            assert "Authorization" in headers
            assert headers["Authorization"].startswith("Bearer ")


def mock_successful_response(data: Any, status_code: int = 200) -> Mock:
    """Create a mock successful HTTP response."""
    response = Mock()
    response.status_code = status_code
    response.json.return_value = data
    response.content = True
    return response


def mock_error_response(status_code: int, error_data: Optional[Dict] = None) -> Mock:
    """Create a mock error HTTP response."""
    response = Mock()
    response.status_code = status_code
    response.json.return_value = error_data or {"detail": "Test error"}
    response.content = bool(error_data)
    return response 