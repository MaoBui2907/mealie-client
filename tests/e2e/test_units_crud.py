"""
E2E Units CRUD Tests

This module tests complete CRUD operations for units including
creation, reading, updating, deletion, and unit management features.
"""

import pytest

from mealie_client.exceptions import NotFoundError

from .utils import assert_unit_equal


class TestE2EUnitsCRUD:
    """Test full CRUD operations for units."""
    
    @pytest.mark.asyncio
    async def test_units_crud_full(self, e2e_test_base, sample_unit_data):
        """Test full CRUD operations for units."""
        client = e2e_test_base.client
        
        # Create unit
        current_units = await client.units.get_all()
        current_units_count = len(current_units)
        
        # Create unit
        created_unit = await client.units.create(sample_unit_data)
        e2e_test_base.track_created_resource('units', created_unit.id)
        
        # Verify creation
        assert created_unit is not None
        assert created_unit.id is not None
        assert_unit_equal(created_unit, sample_unit_data)

        # Verify pagination
        all_units = await client.units.get_all()
        assert len(all_units) == current_units_count + 1

        # Verify search
        search_units = await client.units.get_all(search=sample_unit_data["name"])
        assert len(search_units) == 1
        assert_unit_equal(search_units[0], sample_unit_data)

        # Verify update
        await client.units.update(created_unit.id, {
            "name": "Updated Unit",
        })
        get_unit = await client.units.get(created_unit.id)
        assert get_unit.name == "Updated Unit"

        # Verify delete
        deleted = await client.units.delete(created_unit.id)
        assert deleted
        with pytest.raises(NotFoundError):
            await client.units.get(created_unit.id)

        # Verify get
        with pytest.raises(NotFoundError):
            await client.units.get(created_unit.id)

        # Verify get all
        all_units = await client.units.get_all()
        assert len(all_units) == current_units_count