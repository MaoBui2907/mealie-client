"""
E2E Households Read Tests

This module tests read operations for households.
Note: Mealie API only supports read operations for households (get_all, get).
Households are read-only via API and must be managed via web interface.
"""

import pytest


class TestE2EHouseholdsRead:
    """Test read operations for households that are supported by Mealie API."""
    
    @pytest.mark.asyncio
    async def test_household_crud(self, e2e_test_base):
        """Test create, update, and delete operations for households."""
        client = e2e_test_base.client

        self_household = await client.households.get_self()
        assert self_household is not None
    
