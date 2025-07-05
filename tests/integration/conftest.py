"""
Additional fixtures for integration tests.

This module provides specialized fixtures for integration testing,
including HTTP mocking scenarios and complex test data.
"""

from datetime import datetime, timedelta

import pytest
import respx
import httpx

from mealie_client import MealieClient


# Test URLs and endpoints
TEST_API_BASE = "https://test.mealie.com/api"
TEST_RECIPES_ENDPOINT = f"{TEST_API_BASE}/recipes"
TEST_AUTH_ENDPOINT = f"{TEST_API_BASE}/auth/token"
TEST_USERS_ENDPOINT = f"{TEST_API_BASE}/users"


@pytest.fixture
def mock_server_responses():
    """Mock server responses for various endpoints."""
    return {
        "health": {"status": "ok", "message": "API is healthy"},
        "app_info": {
            "name": "Mealie Test Instance",
            "version": "1.0.0",
            "api_version": "v1",
            "description": "Test Mealie API"
        },
        "login_success": {
            "access_token": "test_access_token_12345",
            "refresh_token": "test_refresh_token_67890",
            "token_type": "bearer",
            "expires_in": 3600
        },
        "login_error": {
            "detail": "Invalid credentials"
        },
        "recipe_created": {
            "id": "recipe_123",
            "name": "Test Recipe",
            "slug": "test-recipe",
            "description": "A test recipe",
            "created_at": datetime.utcnow().isoformat()
        }
    }


@pytest.fixture
def integration_httpx_mock():
    """Enhanced HTTP mock for integration testing with realistic scenarios."""
    with respx.mock(
        base_url="https://test.mealie.com",
        assert_all_called=False,
        assert_all_mocked=True
    ) as mock:
        # Mock health endpoint
        mock.get("/api/app/about").mock(
            return_value=httpx.Response(200, json={"status": "ok"})
        )
        
        # Mock authentication endpoints
        mock.post("/api/auth/token").mock(
            return_value=httpx.Response(200, json={
                "access_token": "test_access_token",
                "refresh_token": "test_refresh_token", 
                "token_type": "bearer",
                "expires_in": 3600
            })
        )
        
        yield mock


@pytest.fixture
async def connected_client(base_url, test_credentials):
    """Create a connected MealieClient for integration testing."""
    client = MealieClient(
        base_url=base_url,
        username=test_credentials["username"],
        password=test_credentials["password"],
        timeout=5.0
    )
    
    # Don't start session automatically - let tests control this
    yield client
    
    # Cleanup
    if client._session_started:
        await client.close_session()


@pytest.fixture
async def authenticated_client(integration_httpx_mock, connected_client):
    """Create an authenticated client ready for API calls."""
    await connected_client.start_session()
    yield connected_client


@pytest.fixture
def mock_recipe_data():
    """Generate realistic recipe data for testing."""
    return {
        "name": "Integration Test Recipe",
        "description": "A recipe created during integration testing",
        "recipe_ingredient": [
            {
                "title": "Main Ingredients",
                "text": "2 cups flour",
                "quantity": 2.0,
                "unit": "cups",
                "food": "flour"
            },
            {
                "title": "Main Ingredients", 
                "text": "1 cup sugar",
                "quantity": 1.0,
                "unit": "cup",
                "food": "sugar"
            }
        ],
        "recipe_instructions": [
            {
                "id": "step_1",
                "title": "Preparation",
                "text": "Mix dry ingredients in a large bowl"
            },
            {
                "id": "step_2", 
                "title": "Mixing",
                "text": "Add wet ingredients and mix until combined"
            }
        ],
        "prep_time": "PT15M",
        "cook_time": "PT30M",
        "total_time": "PT45M",
        "recipe_yield": "8 servings",
        "tags": [{"name": "test"}, {"name": "integration"}],
        "recipe_category": [{"name": "Desserts"}],
        "tools": [{"name": "mixing bowl"}, {"name": "oven"}]
    }


@pytest.fixture
def network_error_scenarios():
    """Define various network error scenarios for testing."""
    return {
        "timeout": httpx.TimeoutException("Request timed out"),
        "connection_error": httpx.ConnectError("Connection failed"),
        "server_error": httpx.Response(500, json={"error": "Internal server error"}),
        "not_found": httpx.Response(404, json={"error": "Resource not found"}),
        "unauthorized": httpx.Response(401, json={"error": "Unauthorized"}),
        "forbidden": httpx.Response(403, json={"error": "Forbidden"}),
        "rate_limit": httpx.Response(429, json={"error": "Rate limit exceeded"}),
        "validation_error": httpx.Response(422, json={"error": "Validation failed"})
    }


@pytest.fixture 
def mock_pagination_response():
    """Mock paginated API response."""
    return {
        "page": 1,
        "per_page": 50,
        "total": 150,
        "total_pages": 3,
        "items": [
            {
                "id": f"item_{i}",
                "name": f"Test Item {i}",
                "created_at": datetime.utcnow().isoformat()
            }
            for i in range(1, 11)  # 10 items for first page
        ]
    }


@pytest.fixture
def complex_workflow_data():
    """Data for testing complex multi-step workflows."""
    return {
        "user_data": {
            "username": "integration_user",
            "email": "integration@test.com", 
            "full_name": "Integration Test User",
            "password": "test_password_123"
        },
        "recipe_data": {
            "name": "Workflow Test Recipe",
            "description": "Recipe for testing complex workflows",
            "prep_time": "PT20M",
            "cook_time": "PT45M"
        },
        "meal_plan_data": {
            "date": datetime.utcnow().date().isoformat(),
            "entry_type": "dinner",
            "title": "Test Meal Plan Entry"
        },
        "shopping_list_data": {
            "name": "Test Shopping List",
            "items": [
                {"food": "Flour", "quantity": 2.0, "unit": "cups"},
                {"food": "Sugar", "quantity": 1.0, "unit": "cup"},
                {"food": "Eggs", "quantity": 3.0, "unit": "pieces"}
            ]
        }
    }


@pytest.fixture
async def retry_test_mock():
    """Mock that simulates retry scenarios."""
    call_count = 0
    
    def side_effect(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        
        if call_count <= 2:  # Fail first 2 attempts
            raise httpx.ConnectError("Connection failed")
        else:  # Succeed on 3rd attempt
            return httpx.Response(200, json={"success": True, "attempt": call_count})
    
    with respx.mock() as mock:
        mock.get("/api/test-retry").mock(side_effect=side_effect)
        yield mock, call_count


@pytest.fixture
def auth_token_scenarios():
    """Different authentication token scenarios for testing."""
    expired_time = datetime.utcnow() - timedelta(hours=1)
    valid_time = datetime.utcnow() + timedelta(hours=1)
    
    return {
        "valid_token": {
            "access_token": "valid_token_12345",
            "refresh_token": "valid_refresh_67890",
            "token_type": "bearer",
            "expires_in": 3600,
            "expires_at": valid_time.isoformat()
        },
        "expired_token": {
            "access_token": "expired_token_12345", 
            "refresh_token": "expired_refresh_67890",
            "token_type": "bearer",
            "expires_in": 0,
            "expires_at": expired_time.isoformat()
        },
        "invalid_token": {
            "error": "invalid_token",
            "error_description": "The access token is invalid"
        }
    }


class MockAsyncContextManager:
    """Helper class for mocking async context managers."""
    
    def __init__(self, client):
        self.client = client
        
    async def __aenter__(self):
        await self.client.start_session()
        return self.client
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.close_session()


@pytest.fixture
def mock_context_manager_client(connected_client):
    """Client wrapped in mock context manager for testing."""
    return MockAsyncContextManager(connected_client) 