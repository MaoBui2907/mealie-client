"""
Unit tests for Groups endpoint.

Tests only read operations since Mealie API doesn't support
group CRUD operations via API.
"""

import pytest
from unittest.mock import AsyncMock, Mock

from mealie_client.endpoints.groups import GroupsManager
from mealie_client.models.group import Group, GroupSummary
from mealie_client.exceptions import NotFoundError, MealieAPIError


class TestGroupsManager:
    """Test GroupsManager functionality."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock client."""
        client = Mock()
        client.get = AsyncMock()
        return client

    @pytest.fixture
    def groups_manager(self, mock_client):
        """Create GroupsManager instance."""
        return GroupsManager(mock_client)

    @pytest.mark.asyncio
    async def test_get_all_groups_with_list_response(self, groups_manager, mock_client):
        """Test getting all groups when API returns a list."""
        mock_groups_data = [
            {"id": "1", "name": "Group 1", "slug": "group-1"},
            {"id": "2", "name": "Group 2", "slug": "group-2"}
        ]
        mock_client.get.return_value = mock_groups_data

        groups = await groups_manager.get_all()

        mock_client.get.assert_called_once_with("admin/groups", params={"page": 1, "perPage": 50, "orderByNullPosition": "last"})
        assert len(groups) == 2
        assert all(isinstance(group, GroupSummary) for group in groups)

    @pytest.mark.asyncio
    async def test_get_all_groups_with_items_response(self, groups_manager, mock_client):
        """Test getting all groups when API returns items wrapper."""
        mock_groups_data = [
            {"id": "1", "name": "Group 1", "slug": "group-1"},
            {"id": "2", "name": "Group 2", "slug": "group-2"}
        ]
        mock_client.get.return_value = {"items": mock_groups_data}

        groups = await groups_manager.get_all()

        mock_client.get.assert_called_once_with("admin/groups", params={"page": 1, "perPage": 50, "orderByNullPosition": "last"})
        assert len(groups) == 2
        assert all(isinstance(group, GroupSummary) for group in groups)

    @pytest.mark.asyncio
    async def test_get_all_groups_empty_response(self, groups_manager, mock_client):
        """Test getting all groups with empty response."""
        mock_client.get.return_value = []

        groups = await groups_manager.get_all()

        mock_client.get.assert_called_once_with("admin/groups", params={"page": 1, "perPage": 50, "orderByNullPosition": "last"})
        assert len(groups) == 0

    @pytest.mark.asyncio
    async def test_get_group_by_id_success(self, groups_manager, mock_client):
        """Test getting a group by ID successfully."""
        mock_group_data = {
            "id": "group-123",
            "name": "Test Group",
            "slug": "test-group",
            "users": [],
            "categories": []
        }
        mock_client.get.return_value = mock_group_data

        group = await groups_manager.get("group-123")

        mock_client.get.assert_called_once_with("admin/groups/group-123")
        assert isinstance(group, Group)
        assert group.id == "group-123"
        assert group.name == "Test Group"

    @pytest.mark.asyncio
    async def test_get_group_by_id_not_found(self, groups_manager, mock_client):
        """Test getting a non-existent group raises NotFoundError."""
        mock_exception = Exception()
        mock_exception.status_code = 404
        mock_client.get.side_effect = mock_exception

        with pytest.raises(NotFoundError) as exc_info:
            await groups_manager.get("nonexistent-group")

        error = exc_info.value
        assert error.details.get("resource_type") == "group"
        assert error.details.get("resource_id") == "nonexistent-group"

    @pytest.mark.asyncio
    async def test_get_group_by_id_other_error(self, groups_manager, mock_client):
        """Test that other errors are re-raised."""
        mock_client.get.side_effect = Exception("Server error")

        with pytest.raises(Exception, match="Server error"):
            await groups_manager.get("group-123")

    # Note: No tests for create, update, delete since they're not supported by Mealie API 