"""
E2E Meal Plans CRUD Tests

This module tests meal plans operations.
Note: Mealie API appears to only support read operations for meal plans.
Create, Update, Delete operations are not supported via API.
"""

import pytest


class TestE2EMealPlansCRUD:
    """Test read operations for meal plans that are supported by Mealie API."""
    
    @pytest.mark.asyncio
    async def test_meal_plans_crud(self, e2e_test_base, sample_meal_plan_data):
        """Test create, update, and delete operations for meal plans."""
        client = e2e_test_base.client

        meal_plans = await client.meal_plans.get_all()
        current_length = len(meal_plans)

        self_household = await client.households.get_self()
        assert self_household is not None
        assert self_household.group_id is not None
        assert self_household.id is not None

        meal_plan = await client.meal_plans.create(
            {
                **sample_meal_plan_data,
                "group_id": self_household.group_id,
                "household_id": self_household.id,
            }
        )
        e2e_test_base.track_created_resource('meal_plans', meal_plan.id)

        meal_plans = await client.meal_plans.get_all()
        assert len(meal_plans) == current_length + 1

        meal_plan = await client.meal_plans.get(meal_plan.id)
        assert meal_plan is not None
        assert meal_plan.title == sample_meal_plan_data["title"]
        assert meal_plan.text == sample_meal_plan_data["text"]
        assert meal_plan.group_id is not None
        assert meal_plan.user_id is not None
        assert meal_plan.household_id is not None
        assert meal_plan.date is not None

        # Update meal plan
        updated_meal_plan = await client.meal_plans.update(
            meal_plan.id,
            {
                "group_id": meal_plan.group_id,
                "user_id": meal_plan.user_id,
                "household_id": meal_plan.household_id,
                "date": meal_plan.date.isoformat(),
                "title": "Updated Meal Plan",
            }
        )
        assert updated_meal_plan.title == "Updated Meal Plan"

        await client.meal_plans.delete(meal_plan.id)
        meal_plans = await client.meal_plans.get_all()
        assert len(meal_plans) == current_length