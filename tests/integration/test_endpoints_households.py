"""
Integration tests for households endpoint.

Tests cover household read operations, error handling, and 
edge cases for the read-only households API.
"""

import pytest
import httpx

from mealie_client.exceptions import NotFoundError, MealieAPIError, AuthorizationError, ConnectionError, TimeoutError


class TestHouseholdsRead:
    """Test suite for household read operations."""

    @pytest.mark.integration
    async def test_get_all_households(self, integration_httpx_mock, authenticated_client):
        """Test fetching all households."""
        households_response = [
            {
                "id": "household_1",
                "name": "Smith Family",
                "slug": "smith-family",
                "created_at": "2023-01-01T00:00:00Z",
                "updated_at": "2023-01-01T00:00:00Z",
                "group_id": "group_123",
                "preferences": {
                    "private_household": False,
                    "first_day_of_week": 0,
                    "recipe_public": True
                }
            },
            {
                "id": "household_2", 
                "name": "Johnson House",
                "slug": "johnson-house",
                "created_at": "2023-01-02T00:00:00Z",
                "updated_at": "2023-01-02T00:00:00Z",
                "group_id": "group_123",
                "preferences": {
                    "private_household": True,
                    "first_day_of_week": 1,
                    "recipe_public": False
                }
            }
        ]
        
        integration_httpx_mock.get("/api/admin/households").mock(
            return_value=httpx.Response(200, json=households_response)
        )
        
        households = await authenticated_client.households.get_all()
        
        assert len(households) == 2
        assert households[0].name == "Smith Family"
        assert households[0].slug == "smith-family"
        assert households[1].name == "Johnson House"
        assert households[1].slug == "johnson-house"

    @pytest.mark.integration
    async def test_get_all_households_paginated_response(self, integration_httpx_mock, authenticated_client):
        """Test households endpoint that returns paginated response format."""
        households_response = {
            "items": [
                {
                    "id": "household_1",
                    "name": "Household One",
                    "slug": "household-one",
                    "group_id": "group_123"
                },
                {
                    "id": "household_2",
                    "name": "Household Two", 
                    "slug": "household-two",
                    "group_id": "group_123"
                }
            ],
            "page": 1,
            "per_page": 50,
            "total": 2
        }
        
        integration_httpx_mock.get("/api/admin/households").mock(
            return_value=httpx.Response(200, json=households_response)
        )
        
        households = await authenticated_client.households.get_all()
        
        assert len(households) == 2
        assert households[0].name == "Household One"
        assert households[1].name == "Household Two"

    @pytest.mark.integration
    async def test_get_all_households_empty(self, integration_httpx_mock, authenticated_client):
        """Test fetching households when none exist."""
        integration_httpx_mock.get("/api/admin/households").mock(
            return_value=httpx.Response(200, json=[])
        )
        
        households = await authenticated_client.households.get_all()
        assert len(households) == 0

    @pytest.mark.integration
    async def test_get_household_by_id(self, integration_httpx_mock, authenticated_client):
        """Test fetching a specific household by ID."""
        household_id = "test-household-123"
        household_data = {
            "id": household_id,
            "name": "Test Household",
            "slug": "test-household",
            "created_at": "2023-01-01T00:00:00Z",
            "updated_at": "2023-01-01T00:00:00Z",
            "group_id": "group_123",
            "preferences": {
                "private_household": False,
                "first_day_of_week": 0,
                "recipe_public": True,
                "recipe_show_nutrition": True,
                "recipe_show_assets": True,
                "recipe_landscape_view": False,
                "recipe_disable_comments": False,
                "recipe_disable_amount": False
            },
            "webhooks": {
                "enabled": False,
                "time": "00:00",
                "url": ""
            },
            "members": [
                {
                    "id": "user_1",
                    "username": "household_admin",
                    "email": "admin@household.com",
                    "role": "admin"
                },
                {
                    "id": "user_2",
                    "username": "household_member",
                    "email": "member@household.com",
                    "role": "member"
                }
            ],
            "shopping_lists": [],
            "meal_plans": []
        }
        
        integration_httpx_mock.get(f"/api/admin/households/{household_id}").mock(
            return_value=httpx.Response(200, json=household_data)
        )
        
        household = await authenticated_client.households.get(household_id)
        
        assert household.id == household_id
        assert household.name == "Test Household"
        assert household.slug == "test-household"
        assert household.preferences is not None
        assert len(household.members) == 2

    @pytest.mark.integration
    async def test_get_household_not_found(self, integration_httpx_mock, authenticated_client):
        """Test handling of non-existent household."""
        household_id = "nonexistent-household"
        integration_httpx_mock.get(f"/api/admin/households/{household_id}").mock(
            return_value=httpx.Response(404, json={"detail": "Household not found"})
        )
        
        with pytest.raises(NotFoundError) as exc_info:
            await authenticated_client.households.get(household_id)
        
        assert exc_info.value.status_code == 404
        assert exc_info.value.resource_type == "household"
        assert exc_info.value.resource_id == household_id

    @pytest.mark.integration
    async def test_get_household_html_response_not_found(self, integration_httpx_mock, authenticated_client):
        """Test handling when Mealie returns HTML for non-existent households."""
        household_id = "html-response-household"
        html_response = b"""<!DOCTYPE html>
        <html>
        <head><title>Mealie</title></head>
        <body>Household not found</body>
        </html>"""
        
        integration_httpx_mock.get(f"/api/admin/households/{household_id}").mock(
            return_value=httpx.Response(200, content=html_response, headers={"content-type": "text/html"})
        )
        
        with pytest.raises(NotFoundError) as exc_info:
            await authenticated_client.households.get(household_id)
        
        assert exc_info.value.resource_type == "household"
        assert exc_info.value.resource_id == household_id


class TestHouseholdsErrorHandling:
    """Test suite for households error handling scenarios."""

    @pytest.mark.integration
    async def test_get_households_server_error(self, integration_httpx_mock, authenticated_client):
        """Test handling of server errors when fetching households."""
        integration_httpx_mock.get("/api/admin/households").mock(
            return_value=httpx.Response(500, json={"detail": "Internal server error"})
        )
        
        with pytest.raises(MealieAPIError) as exc_info:
            await authenticated_client.households.get_all()
        
        assert exc_info.value.status_code == 500

    @pytest.mark.integration
    async def test_get_household_forbidden(self, integration_httpx_mock, authenticated_client):
        """Test handling of forbidden access to household."""
        household_id = "forbidden-household"
        integration_httpx_mock.get(f"/api/admin/households/{household_id}").mock(
            return_value=httpx.Response(403, json={"detail": "Access denied to household"})
        )
        
        with pytest.raises(AuthorizationError) as exc_info:
            await authenticated_client.households.get(household_id)
        
        assert exc_info.value.status_code == 403

    @pytest.mark.integration
    async def test_get_households_network_error(self, integration_httpx_mock, authenticated_client):
        """Test handling of network errors when fetching households."""
        integration_httpx_mock.get("/api/admin/households").mock(
            side_effect=httpx.ConnectError("Network unreachable")
        )
        
        with pytest.raises(ConnectionError) as exc_info:
            await authenticated_client.households.get_all()
        
        assert "Network unreachable" in str(exc_info.value)

    @pytest.mark.integration
    async def test_get_households_timeout(self, integration_httpx_mock, authenticated_client):
        """Test handling of timeout when fetching households."""
        integration_httpx_mock.get("/api/admin/households").mock(
            side_effect=httpx.TimeoutException("Request timed out")
        )
        
        with pytest.raises(TimeoutError) as exc_info:
            await authenticated_client.households.get_all()
        
        assert "Request timed out" in str(exc_info.value)


class TestHouseholdsDataValidation:
    """Test suite for households data validation and edge cases."""

    @pytest.mark.integration
    async def test_get_households_malformed_response(self, integration_httpx_mock, authenticated_client):
        """Test handling of malformed JSON response."""
        integration_httpx_mock.get("/api/admin/households").mock(
            return_value=httpx.Response(
                200, 
                content=b"invalid json content",
                headers={"content-type": "application/json"}
            )
        )
        
        with pytest.raises(ConnectionError):
            await authenticated_client.households.get_all()

    @pytest.mark.integration
    async def test_get_household_partial_data(self, integration_httpx_mock, authenticated_client):
        """Test handling of household response with missing fields."""
        household_id = "partial-household"
        partial_household_data = {
            "id": household_id,
            "name": "Partial Household",
            "group_id": "group_123"
            # Missing slug, created_at, preferences, etc.
        }
        
        integration_httpx_mock.get(f"/api/admin/households/{household_id}").mock(
            return_value=httpx.Response(200, json=partial_household_data)
        )
        
        household = await authenticated_client.households.get(household_id)
        
        assert household.id == household_id
        assert household.name == "Partial Household"
        # Should handle missing fields gracefully

    @pytest.mark.integration
    async def test_get_households_with_complex_structure(self, integration_httpx_mock, authenticated_client):
        """Test households with complex member and resource structures."""
        households_response = [
            {
                "id": "complex_household",
                "name": "Complex Household",
                "slug": "complex-household",
                "group_id": "group_123",
                "preferences": {
                    "private_household": True,
                    "first_day_of_week": 1,
                    "recipe_public": False,
                    "recipe_show_nutrition": True,
                    "recipe_show_assets": False,
                    "recipe_landscape_view": True,
                    "recipe_disable_comments": True,
                    "recipe_disable_amount": False
                },
                "webhooks": {
                    "enabled": True,
                    "time": "09:00",
                    "url": "https://webhook.example.com/household-notifications"
                },
                "members": [
                    {
                        "id": "admin_user",
                        "username": "household_admin",
                        "role": "admin",
                        "permissions": ["read", "write", "delete"]
                    },
                    {
                        "id": "member_user",
                        "username": "household_member",
                        "role": "member", 
                        "permissions": ["read", "write"]
                    }
                ],
                "shopping_lists": [
                    {"id": "list_1", "name": "Weekly Groceries"},
                    {"id": "list_2", "name": "Party Supplies"}
                ],
                "meal_plans": [
                    {"id": "plan_1", "date": "2023-12-25", "title": "Christmas Dinner"}
                ]
            }
        ]
        
        integration_httpx_mock.get("/api/admin/households").mock(
            return_value=httpx.Response(200, json=households_response)
        )
        
        households = await authenticated_client.households.get_all()
        
        assert len(households) == 1
        household = households[0]
        assert household.name == "Complex Household"
        assert hasattr(household, 'preferences')
        assert hasattr(household, 'webhooks')
        assert hasattr(household, 'members')
        assert len(household.members) == 2


class TestHouseholdsReadOnlyValidation:
    """Test suite validating that households are truly read-only."""

    @pytest.mark.integration
    async def test_households_api_endpoints_read_only(self, integration_httpx_mock, authenticated_client):
        """Test that attempting write operations on households fails appropriately."""
        # This test documents the API behavior rather than SDK behavior
        household_data = {
            "name": "New Household",
            "slug": "new-household"
        }
        
        # Mock that the API would reject POST/PUT/DELETE operations
        integration_httpx_mock.post("/api/groups/households").mock(
            return_value=httpx.Response(405, json={"detail": "Method not allowed"})
        )
        
        integration_httpx_mock.put("/api/groups/households/some-id").mock(
            return_value=httpx.Response(405, json={"detail": "Method not allowed"})
        )
        
        integration_httpx_mock.delete("/api/groups/households/some-id").mock(
            return_value=httpx.Response(405, json={"detail": "Method not allowed"})
        )
        
        # Direct API calls should fail (if attempted)
        with pytest.raises(MealieAPIError) as exc_info:
            await authenticated_client.post("groups/households", json_data=household_data)
        assert exc_info.value.status_code == 405


class TestHouseholdsWorkflows:
    """Test suite for household-related workflows."""

    @pytest.mark.integration
    async def test_browse_households_workflow(self, integration_httpx_mock, authenticated_client):
        """Test complete household browsing workflow."""
        # Mock get all households
        households_list = [
            {"id": "household_1", "name": "Household One", "slug": "household-one", "group_id": "group_123"},
            {"id": "household_2", "name": "Household Two", "slug": "household-two", "group_id": "group_123"}
        ]
        
        integration_httpx_mock.get("/api/admin/households").mock(
            return_value=httpx.Response(200, json=households_list)
        )
        
        # Mock get specific household details
        detailed_household = {
            "id": "household_1",
            "name": "Household One",
            "slug": "household-one",
            "group_id": "group_123",
            "created_at": "2023-01-01T00:00:00Z",
            "preferences": {
                "private_household": False,
                "recipe_public": True
            },
            "members": [
                {"id": "user_1", "username": "admin", "role": "admin"},
                {"id": "user_2", "username": "member", "role": "member"}
            ],
            "shopping_lists": [
                {"id": "list_1", "name": "Groceries"},
                {"id": "list_2", "name": "Cleaning Supplies"}
            ],
            "meal_plans": [
                {"id": "plan_1", "date": "2023-12-25", "title": "Holiday Meal"}
            ]
        }
        
        integration_httpx_mock.get("/api/admin/households/household_1").mock(
            return_value=httpx.Response(200, json=detailed_household)
        )
        
        # Execute workflow
        # 1. Browse available households
        households = await authenticated_client.households.get_all()
        assert len(households) == 2
        
        # 2. Get details of specific household
        household = await authenticated_client.households.get("household_1")
        assert household.name == "Household One"
        assert hasattr(household, 'members')
        assert hasattr(household, 'shopping_lists')
        assert hasattr(household, 'meal_plans')

    @pytest.mark.integration
    async def test_household_discovery_with_error_recovery(self, integration_httpx_mock, authenticated_client):
        """Test household discovery with error recovery workflow."""
        # First attempt fails
        integration_httpx_mock.get("/api/admin/households").mock(
            return_value=httpx.Response(503, json={"detail": "Service temporarily unavailable"})
        )
        
        # First attempt should fail
        with pytest.raises(MealieAPIError):
            await authenticated_client.households.get_all()
        
        # Second attempt succeeds
        households_response = [
            {"id": "recovered_household", "name": "Recovered Household", "slug": "recovered-household", "group_id": "group_123"}
        ]
        
        integration_httpx_mock.get("/api/admin/households").mock(
            return_value=httpx.Response(200, json=households_response)
        )
        
        # Recovery should work
        households = await authenticated_client.households.get_all()
        assert len(households) == 1
        assert households[0].name == "Recovered Household"

    @pytest.mark.integration
    async def test_household_member_and_resource_inspection(self, integration_httpx_mock, authenticated_client):
        """Test inspecting household members and resources workflow."""
        household_id = "inspection-household"
        
        # Mock detailed household with rich information
        detailed_household = {
            "id": household_id,
            "name": "Family Household",
            "slug": "family-household",
            "group_id": "group_123",
            "members": [
                {
                    "id": "dad",
                    "username": "dad_user",
                    "email": "dad@family.com",
                    "full_name": "Dad User",
                    "role": "admin",
                    "permissions": ["read", "write", "delete", "admin"]
                },
                {
                    "id": "mom",
                    "username": "mom_user", 
                    "email": "mom@family.com",
                    "full_name": "Mom User",
                    "role": "admin",
                    "permissions": ["read", "write", "delete", "admin"]
                },
                {
                    "id": "kid",
                    "username": "kid_user",
                    "email": "kid@family.com",
                    "full_name": "Kid User",
                    "role": "member",
                    "permissions": ["read"]
                }
            ],
            "shopping_lists": [
                {"id": "weekly", "name": "Weekly Groceries", "created_by": "dad"},
                {"id": "party", "name": "Birthday Party", "created_by": "mom"}
            ],
            "meal_plans": [
                {"id": "week1", "date": "2023-12-25", "title": "Christmas Week", "created_by": "mom"},
                {"id": "week2", "date": "2024-01-01", "title": "New Year Week", "created_by": "dad"}
            ]
        }
        
        integration_httpx_mock.get(f"/api/admin/households/{household_id}").mock(
            return_value=httpx.Response(200, json=detailed_household)
        )
        
        # Execute inspection workflow
        household = await authenticated_client.households.get(household_id)
        
        # Verify rich household information
        assert household.name == "Family Household"
        assert len(household.members) == 3
        
        # Check member roles
        admin_members = [m for m in household.members if m["role"] == "admin"]
        regular_members = [m for m in household.members if m["role"] == "member"]
        assert len(admin_members) == 2
        assert len(regular_members) == 1
        
        # Check resources
        assert len(household.shopping_lists) == 2
        assert len(household.meal_plans) == 2 