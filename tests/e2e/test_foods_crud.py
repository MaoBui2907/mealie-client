"""
E2E Foods CRUD Tests

This module tests complete CRUD operations for foods including
creation, reading, updating, deletion, and food management features.
"""

import pytest
from mealie_client.exceptions import NotFoundError
from mealie_client import MealieClient

from .utils import assert_food_equal


class TestE2EFoodsCRUD:
    """Test full CRUD operations for foods."""
    
    @pytest.mark.asyncio
    async def test_foods_crud_full(self, e2e_test_base, sample_food_data):
        """Test full CRUD operations for foods."""
        client: MealieClient = e2e_test_base.client
        
        # Create food
        current_foods = await client.foods.get_all()
        current_foods_count = len(current_foods)
        
        # Create food
        created_food = await client.foods.create(sample_food_data)
        e2e_test_base.track_created_resource('foods', created_food.id)
        
        # Verify creation
        all_foods = await client.foods.get_all()
        assert len(all_foods) == current_foods_count + 1

        get_created_food = await client.foods.get(created_food.id)
        assert_food_equal(get_created_food, sample_food_data)

        # Verify search
        search_foods = await client.foods.get_all(search=sample_food_data["name"], page=1, per_page=1)
        assert len(search_foods) == 1
        assert_food_equal(search_foods[0], sample_food_data)

        # Verify update
        await client.foods.update(created_food.id, {
            "name": "Updated Food",
        })
        get_updated_food = await client.foods.get(created_food.id)
        assert get_updated_food.name == "Updated Food"

        # Verify delete
        deleted = await client.foods.delete(created_food.id)
        assert deleted
        with pytest.raises(NotFoundError):
            await client.foods.get(created_food.id)

        # Verify get
        with pytest.raises(NotFoundError):
            await client.foods.get(created_food.id)

        # Verify get all
        all_foods = await client.foods.get_all()
        assert len(all_foods) == current_foods_count