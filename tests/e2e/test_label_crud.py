"""
E2E Labels CRUD Tests

This module tests CRUD operations for labels.
"""

import pytest

class TestE2ELabelsCRUD:
    """Test read operations for labels that are supported by Mealie API."""
    
    @pytest.mark.asyncio
    async def test_label_crud(self, e2e_test_base, sample_label_data):
        """Test create, update, and delete operations for labels."""
        client = e2e_test_base.client

        all_labels = await client.labels.get_all()
        current_label_count = len(all_labels)

        label = await client.labels.create(sample_label_data)
        assert label is not None

        all_labels = await client.labels.get_all()
        assert len(all_labels) == current_label_count + 1

        updated_label = await client.labels.update(label.id, {
            "name": "Updated Test Label",
            "color": "#000000",
            "group_id": label.group_id,
            "id": label.id,
        })
        assert updated_label is not None
        assert updated_label.name == "Updated Test Label"
        assert updated_label.color == "#000000"

        label = await client.labels.get(label.id)
        assert label is not None

        await client.labels.delete(label.id)
        all_labels = await client.labels.get_all()
        assert len(all_labels) == current_label_count
