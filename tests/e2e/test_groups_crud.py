"""
E2E Groups Read Tests

This module tests read operations for groups. 
Note: Mealie API only supports read operations for groups (get_all, get).
CRUD operations (create, update, delete) must be performed via web interface.
"""

import pytest
from tests.e2e.utils.assertions import assert_group_equal


class TestE2EGroupsRead:
    """Test read operations for groups that are supported by Mealie API."""
    
    @pytest.mark.asyncio
    @pytest.mark.skip(reason="CRUD operations are not supported by Mealie API.")
    async def test_groups_crud_full(self, e2e_test_base, sample_group_data):
        """Test full CRUD operations for groups."""
        client = e2e_test_base.client

        # Get all groups
        all_groups = await client.groups.get_all()
        current_groups_count = len(all_groups)

        # Create a group
        group = await client.groups.create(sample_group_data)
        e2e_test_base.track_created_resource('groups', group.id)

        # Verify creation
        all_groups = await client.groups.get_all()
        assert len(all_groups) == current_groups_count + 1

        # Verify get
        get_group = await client.groups.get(group.id)
        assert_group_equal(get_group, sample_group_data)

        # Verify update
        updated_group = await client.groups.update(group.id, {
            "name": "Updated Group",
        })
        assert updated_group.name == "Updated Group"

        # TODO: VERIFY DELETE GROUP. IT NOT WORKING.
        # Verify delete
        # await client.groups.delete(group.id)
        # with pytest.raises(NotFoundError):
        #     await client.groups.get(group.id)

        # Verify get all again
        # all_groups = await client.groups.get_all()
        # assert len(all_groups) == current_groups_count

    @pytest.mark.asyncio
    async def test_groups_self(self, e2e_test_base):
        """Test get self for groups."""
        client = e2e_test_base.client
        group = await client.groups.get_self()
        assert group is not None
        assert group.name == "Home"
        assert group.slug == "home"

        # Verify get group preferences
        preferences = await client.groups.get_group_preferences()
        assert preferences is not None