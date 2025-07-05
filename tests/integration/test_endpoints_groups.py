"""
Integration tests for groups endpoint.

Tests cover group read operations, error handling, and 
edge cases for the read-only groups API.
"""

import pytest
import httpx

from mealie_client.exceptions import NotFoundError, MealieAPIError, AuthorizationError, ConnectionError, TimeoutError


class TestGroupsRead:
    """Test suite for group read operations."""

    @pytest.mark.integration
    async def test_get_all_groups(self, integration_httpx_mock, authenticated_client):
        """Test fetching all groups."""
        groups_response = [
            {
                "id": "group_1",
                "name": "Default Group",
                "slug": "default-group",
                "created_at": "2023-01-01T00:00:00Z",
                "updated_at": "2023-01-01T00:00:00Z",
                "preferences": {
                    "private_group": False,
                    "first_day_of_week": 0,
                    "recipe_public": True
                }
            },
            {
                "id": "group_2", 
                "name": "Family Group",
                "slug": "family-group",
                "created_at": "2023-01-02T00:00:00Z",
                "updated_at": "2023-01-02T00:00:00Z",
                "preferences": {
                    "private_group": True,
                    "first_day_of_week": 1,
                    "recipe_public": False
                }
            }
        ]
        
        integration_httpx_mock.get("/api/admin/groups").mock(
            return_value=httpx.Response(200, json=groups_response)
        )
        
        groups = await authenticated_client.groups.get_all()
        
        assert len(groups) == 2
        assert groups[0].name == "Default Group"
        assert groups[0].slug == "default-group"
        assert groups[1].name == "Family Group"
        assert groups[1].slug == "family-group"

    @pytest.mark.integration
    async def test_get_all_groups_paginated_response(self, integration_httpx_mock, authenticated_client):
        """Test groups endpoint that returns paginated response format."""
        groups_response = {
            "items": [
                {
                    "id": "group_1",
                    "name": "Group One",
                    "slug": "group-one"
                },
                {
                    "id": "group_2",
                    "name": "Group Two", 
                    "slug": "group-two"
                }
            ],
            "page": 1,
            "per_page": 50,
            "total": 2
        }
        
        integration_httpx_mock.get("/api/admin/groups").mock(
            return_value=httpx.Response(200, json=groups_response)
        )
        
        groups = await authenticated_client.groups.get_all()
        
        assert len(groups) == 2
        assert groups[0].name == "Group One"
        assert groups[1].name == "Group Two"

    @pytest.mark.integration
    async def test_get_all_groups_empty(self, integration_httpx_mock, authenticated_client):
        """Test fetching groups when none exist."""
        integration_httpx_mock.get("/api/admin/groups").mock(
            return_value=httpx.Response(200, json=[])
        )
        
        groups = await authenticated_client.groups.get_all()
        assert len(groups) == 0

    @pytest.mark.integration
    async def test_get_group_by_id(self, integration_httpx_mock, authenticated_client):
        """Test fetching a specific group by ID."""
        group_id = "test-group-123"
        group_data = {
            "id": group_id,
            "name": "Test Group",
            "slug": "test-group",
            "created_at": "2023-01-01T00:00:00Z",
            "updated_at": "2023-01-01T00:00:00Z",
            "preferences": {
                "private_group": False,
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
            "categories": [],
            "tags": [],
            "tools": [],
            "households": []
        }
        
        integration_httpx_mock.get(f"/api/admin/groups/{group_id}").mock(
            return_value=httpx.Response(200, json=group_data)
        )
        
        group = await authenticated_client.groups.get(group_id)
        
        assert group.id == group_id
        assert group.name == "Test Group"
        assert group.slug == "test-group"
        assert group.preferences is not None

    @pytest.mark.integration
    async def test_get_group_not_found(self, integration_httpx_mock, authenticated_client):
        """Test handling of non-existent group."""
        group_id = "nonexistent-group"
        integration_httpx_mock.get(f"/api/admin/groups/{group_id}").mock(
            return_value=httpx.Response(404, json={"detail": "Group not found"})
        )
        
        with pytest.raises(NotFoundError) as exc_info:
            await authenticated_client.groups.get(group_id)
        
        assert exc_info.value.status_code == 404
        assert exc_info.value.resource_type == "group"
        assert exc_info.value.resource_id == group_id

    @pytest.mark.integration
    async def test_get_group_html_response_not_found(self, integration_httpx_mock, authenticated_client):
        """Test handling when Mealie returns HTML for non-existent groups."""
        group_id = "html-response-group"
        html_response = b"""<!DOCTYPE html>
        <html>
        <head><title>Mealie</title></head>
        <body>Group not found</body>
        </html>"""
        
        integration_httpx_mock.get(f"/api/admin/groups/{group_id}").mock(
            return_value=httpx.Response(200, content=html_response, headers={"content-type": "text/html"})
        )
        
        with pytest.raises(NotFoundError) as exc_info:
            await authenticated_client.groups.get(group_id)
        
        assert exc_info.value.resource_type == "group"
        assert exc_info.value.resource_id == group_id


class TestGroupsErrorHandling:
    """Test suite for groups error handling scenarios."""

    @pytest.mark.integration
    async def test_get_groups_server_error(self, integration_httpx_mock, authenticated_client):
        """Test handling of server errors when fetching groups."""
        integration_httpx_mock.get("/api/admin/groups").mock(
            return_value=httpx.Response(500, json={"detail": "Internal server error"})
        )
        
        with pytest.raises(MealieAPIError) as exc_info:
            await authenticated_client.groups.get_all()
        
        assert exc_info.value.status_code == 500

    @pytest.mark.integration
    async def test_get_group_forbidden(self, integration_httpx_mock, authenticated_client):
        """Test handling of forbidden access to group."""
        group_id = "forbidden-group"
        integration_httpx_mock.get(f"/api/admin/groups/{group_id}").mock(
            return_value=httpx.Response(403, json={"detail": "Access denied"})
        )
        
        with pytest.raises(AuthorizationError) as exc_info:
            await authenticated_client.groups.get(group_id)
        
        assert exc_info.value.status_code == 403

    @pytest.mark.integration
    async def test_get_groups_network_error(self, integration_httpx_mock, authenticated_client):
        """Test handling of network errors when fetching groups."""
        integration_httpx_mock.get("/api/admin/groups").mock(
            side_effect=httpx.ConnectError("Network unreachable")
        )
        
        with pytest.raises(ConnectionError) as exc_info:
            await authenticated_client.groups.get_all()
        
        assert "Network unreachable" in str(exc_info.value)

    @pytest.mark.integration
    async def test_get_groups_timeout(self, integration_httpx_mock, authenticated_client):
        """Test handling of timeout when fetching groups."""
        integration_httpx_mock.get("/api/admin/groups").mock(
            side_effect=httpx.TimeoutException("Request timed out")
        )
        
        with pytest.raises(TimeoutError) as exc_info:
            await authenticated_client.groups.get_all()
        
        assert "Request timed out" in str(exc_info.value)


class TestGroupsDataValidation:
    """Test suite for groups data validation and edge cases."""

    @pytest.mark.integration
    async def test_get_groups_malformed_response(self, integration_httpx_mock, authenticated_client):
        """Test handling of malformed JSON response."""
        integration_httpx_mock.get("/api/admin/groups").mock(
            return_value=httpx.Response(
                200, 
                content=b"invalid json content",
                headers={"content-type": "application/json"}
            )
        )
        
        with pytest.raises(ConnectionError):
            await authenticated_client.groups.get_all()

    @pytest.mark.integration
    async def test_get_group_partial_data(self, integration_httpx_mock, authenticated_client):
        """Test handling of group response with missing fields."""
        group_id = "partial-group"
        partial_group_data = {
            "id": group_id,
            "name": "Partial Group"
            # Missing slug, created_at, preferences, etc.
        }
        
        integration_httpx_mock.get(f"/api/admin/groups/{group_id}").mock(
            return_value=httpx.Response(200, json=partial_group_data)
        )
        
        group = await authenticated_client.groups.get(group_id)
        
        assert group.id == group_id
        assert group.name == "Partial Group"
        # Should handle missing fields gracefully

    @pytest.mark.integration
    async def test_get_groups_with_complex_preferences(self, integration_httpx_mock, authenticated_client):
        """Test groups with complex preference configurations."""
        groups_response = [
            {
                "id": "complex_group",
                "name": "Complex Group",
                "slug": "complex-group",
                "preferences": {
                    "private_group": True,
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
                    "url": "https://webhook.example.com/notifications"
                }
            }
        ]
        
        integration_httpx_mock.get("/api/admin/groups").mock(
            return_value=httpx.Response(200, json=groups_response)
        )
        
        groups = await authenticated_client.groups.get_all()
        
        assert len(groups) == 1
        group = groups[0]
        assert group.name == "Complex Group"
        assert hasattr(group, 'preferences')
        assert hasattr(group, 'webhooks')


class TestGroupsReadOnlyValidation:
    """Test suite validating that groups are truly read-only."""
    @pytest.mark.integration
    async def test_groups_api_endpoints_read_only(self, integration_httpx_mock, authenticated_client):
        """Test that attempting write operations on groups fails appropriately."""
        # This test documents the API behavior rather than SDK behavior
        group_data = {
            "name": "New Group",
            "slug": "new-group"
        }
        
        # Mock that the API would reject POST/PUT/DELETE operations
        integration_httpx_mock.post("/api/groups").mock(
            return_value=httpx.Response(405, json={"detail": "Method not allowed"})
        )
        
        integration_httpx_mock.put("/api/groups/some-id").mock(
            return_value=httpx.Response(405, json={"detail": "Method not allowed"})
        )
        
        integration_httpx_mock.delete("/api/groups/some-id").mock(
            return_value=httpx.Response(405, json={"detail": "Method not allowed"})
        )
        
        # Direct API calls should fail (if attempted)
        with pytest.raises(MealieAPIError) as exc_info:
            await authenticated_client.post("groups", json_data=group_data)
        assert exc_info.value.status_code == 405


class TestGroupsWorkflows:
    """Test suite for group-related workflows."""

    @pytest.mark.integration
    async def test_browse_groups_workflow(self, integration_httpx_mock, authenticated_client):
        """Test complete group browsing workflow."""
        # Mock get all groups
        groups_list = [
            {"id": "group_1", "name": "Group One", "slug": "group-one"},
            {"id": "group_2", "name": "Group Two", "slug": "group-two"}
        ]
        
        integration_httpx_mock.get("/api/admin/groups").mock(
            return_value=httpx.Response(200, json=groups_list)
        )
        
        # Mock get specific group details
        detailed_group = {
            "id": "group_1",
            "name": "Group One",
            "slug": "group-one",
            "created_at": "2023-01-01T00:00:00Z",
            "preferences": {
                "private_group": False,
                "recipe_public": True
            },
            "categories": [
                {"id": "cat_1", "name": "Appetizers"},
                {"id": "cat_2", "name": "Main Courses"}
            ],
            "tags": [
                {"id": "tag_1", "name": "Quick"},
                {"id": "tag_2", "name": "Healthy"}
            ]
        }
        
        integration_httpx_mock.get("/api/admin/groups/group_1").mock(
            return_value=httpx.Response(200, json=detailed_group)
        )
        
        # Execute workflow
        # 1. Browse available groups
        groups = await authenticated_client.groups.get_all()
        assert len(groups) == 2
        
        # 2. Get details of specific group
        group = await authenticated_client.groups.get("group_1")
        assert group.name == "Group One"
        assert hasattr(group, 'categories')
        assert hasattr(group, 'tags')

    @pytest.mark.integration
    async def test_group_discovery_with_error_recovery(self, integration_httpx_mock, authenticated_client):
        """Test group discovery with error recovery workflow."""
        # First attempt fails
        integration_httpx_mock.get("/api/admin/groups").mock(
            return_value=httpx.Response(503, json={"detail": "Service temporarily unavailable"})
        )
        
        # First attempt should fail
        with pytest.raises(MealieAPIError):
            await authenticated_client.groups.get_all()
        
        # Second attempt succeeds
        groups_response = [
            {"id": "recovered_group", "name": "Recovered Group", "slug": "recovered-group"}
        ]
        
        integration_httpx_mock.get("/api/admin/groups").mock(
            return_value=httpx.Response(200, json=groups_response)
        )
        
        # Recovery should work
        groups = await authenticated_client.groups.get_all()
        assert len(groups) == 1
        assert groups[0].name == "Recovered Group" 