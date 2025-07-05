"""
Integration tests for meal plans endpoint.

Tests cover meal plan CRUD operations, date filtering,
validation scenarios, and meal planning workflows.
"""

from datetime import date, datetime, timedelta

import pytest
import httpx

from mealie_client.exceptions import NotFoundError, ValidationError, AuthorizationError


class TestMealPlansCRUD:
    """Test suite for basic meal plan CRUD operations."""

    @pytest.mark.integration
    async def test_get_all_meal_plans(self, integration_httpx_mock, authenticated_client):
        """Test fetching all meal plans."""
        meal_plans_response = [
            {
                "id": "plan_1",
                "date": "2023-12-25",
                "entry_type": "dinner",
                "title": "Christmas Dinner",
                "recipe_id": "recipe_123",
                "recipe": {
                    "id": "recipe_123",
                    "name": "Roast Turkey",
                    "slug": "roast-turkey"
                },
                "created_at": "2023-12-01T00:00:00Z",
                "updated_at": "2023-12-01T00:00:00Z"
            },
            {
                "id": "plan_2",
                "date": "2023-12-26",
                "entry_type": "lunch",
                "title": "Turkey Sandwiches",
                "recipe_id": "recipe_456",
                "recipe": {
                    "id": "recipe_456",
                    "name": "Turkey Sandwich",
                    "slug": "turkey-sandwich"
                },
                "created_at": "2023-12-01T00:00:00Z",
                "updated_at": "2023-12-01T00:00:00Z"
            }
        ]
        
        integration_httpx_mock.get("/api/households/mealplans").mock(
            return_value=httpx.Response(200, json=meal_plans_response)
        )
        
        meal_plans = await authenticated_client.meal_plans.get_all()
        
        assert len(meal_plans) == 2
        assert meal_plans[0].title == "Christmas Dinner"
        assert meal_plans[0].entry_type == "dinner"
        assert meal_plans[1].title == "Turkey Sandwiches"
        assert meal_plans[1].entry_type == "lunch"

    @pytest.mark.integration
    async def test_get_meal_plans_with_date_filtering(self, integration_httpx_mock, authenticated_client):
        """Test fetching meal plans with date range filtering."""
        start_date = date(2023, 12, 25)
        end_date = date(2023, 12, 31)
        
        filtered_plans = [
            {
                "id": "plan_filtered",
                "date": "2023-12-25",
                "entry_type": "dinner",
                "title": "Christmas Dinner",
                "recipe_id": "recipe_123"
            }
        ]
        
        integration_httpx_mock.get("/api/households/mealplans").mock(
            return_value=httpx.Response(200, json=filtered_plans)
        )
        
        meal_plans = await authenticated_client.meal_plans.get_all(
            start_date=start_date,
            end_date=end_date
        )
        
        assert len(meal_plans) == 1
        assert str(meal_plans[0].date) == "2023-12-25"

    @pytest.mark.integration
    async def test_get_meal_plans_paginated_response(self, integration_httpx_mock, authenticated_client):
        """Test meal plans endpoint that returns paginated response format."""
        paginated_response = {
            "items": [
                {
                    "id": "plan_paged_1",
                    "date": "2023-12-25",
                    "entry_type": "breakfast",
                    "title": "Holiday Pancakes"
                }
            ],
            "page": 1,
            "per_page": 50,
            "total": 1
        }
        
        integration_httpx_mock.get("/api/households/mealplans").mock(
            return_value=httpx.Response(200, json=paginated_response)
        )
        
        meal_plans = await authenticated_client.meal_plans.get_all()
        
        assert len(meal_plans) == 1
        assert meal_plans[0].title == "Holiday Pancakes"

    @pytest.mark.integration
    async def test_get_meal_plan_by_id(self, integration_httpx_mock, authenticated_client):
        """Test fetching a specific meal plan by ID."""
        plan_id = "test-plan-123"
        plan_data = {
            "id": plan_id,
            "date": "2023-12-25",
            "entry_type": "dinner",
            "title": "Christmas Dinner",
            "text": "Special holiday meal with family",
            "recipe_id": "recipe_123",
            "recipe": {
                "id": "recipe_123",
                "name": "Roast Turkey",
                "slug": "roast-turkey",
                "image": "turkey.jpg"
            },
            "created_at": "2023-12-01T00:00:00Z",
            "updated_at": "2023-12-01T00:00:00Z"
        }
        
        integration_httpx_mock.get(f"/api/households/mealplans/{plan_id}").mock(
            return_value=httpx.Response(200, json=plan_data)
        )
        
        meal_plan = await authenticated_client.meal_plans.get(plan_id)
        
        assert meal_plan.id == plan_id
        assert meal_plan.title == "Christmas Dinner"
        assert meal_plan.entry_type == "dinner"
        assert str(meal_plan.date) == "2023-12-25"

    @pytest.mark.integration
    async def test_get_meal_plan_not_found(self, integration_httpx_mock, authenticated_client):
        """Test handling of non-existent meal plan."""
        plan_id = "nonexistent-plan"
        integration_httpx_mock.get(f"/api/households/mealplans/{plan_id}").mock(
            return_value=httpx.Response(404, json={"detail": "Meal plan not found"})
        )
        
        with pytest.raises(NotFoundError) as exc_info:
            await authenticated_client.meal_plans.get(plan_id)
        
        assert exc_info.value.status_code == 404
        assert exc_info.value.resource_type == "meal_plan"
        assert exc_info.value.resource_id == plan_id

    @pytest.mark.integration
    async def test_create_meal_plan_success(self, integration_httpx_mock, authenticated_client):
        """Test successful meal plan creation."""
        plan_data = {
            "date": "2023-12-25",
            "entry_type": "dinner",
            "title": "New Christmas Dinner",
            "text": "Planning a special meal",
            "recipe_id": "recipe_789"
        }
        
        created_plan = {
            "id": "new-plan-456",
            **plan_data,
            "created_at": "2023-12-01T00:00:00Z",
            "updated_at": "2023-12-01T00:00:00Z"
        }
        
        integration_httpx_mock.post("/api/households/mealplans").mock(
            return_value=httpx.Response(201, json=created_plan)
        )
        
        meal_plan = await authenticated_client.meal_plans.create(plan_data)
        
        assert meal_plan.id == "new-plan-456"
        assert meal_plan.title == "New Christmas Dinner"
        assert str(meal_plan.date) == "2023-12-25"

    @pytest.mark.integration
    async def test_create_meal_plan_validation_error(self, integration_httpx_mock, authenticated_client):
        """Test meal plan creation with validation errors."""
        integration_httpx_mock.post("/api/households/mealplans").mock(
            return_value=httpx.Response(422, json={
                "detail": [
                    {"loc": ["date"], "msg": "field required", "type": "value_error.missing"},
                    {"loc": ["entry_type"], "msg": "invalid entry type", "type": "value_error"}
                ]
            })
        )
        
        with pytest.raises(ValidationError) as exc_info:
            await authenticated_client.meal_plans.create({"title": "Invalid Plan"})
        
        assert exc_info.value.status_code == 422
        assert "field required" in str(exc_info.value)

    @pytest.mark.integration
    async def test_update_meal_plan_success(self, integration_httpx_mock, authenticated_client):
        """Test successful meal plan update."""
        plan_id = "update-plan-789"
        update_data = {
            "title": "Updated Christmas Dinner",
            "text": "Updated meal planning notes",
            "recipe_id": "recipe_999"
        }
        
        updated_plan = {
            "id": plan_id,
            "date": "2023-12-25",
            "entry_type": "dinner",
            **update_data,
            "updated_at": "2023-12-01T12:00:00Z"
        }
        
        integration_httpx_mock.put(f"/api/households/mealplans/{plan_id}").mock(
            return_value=httpx.Response(200, json=updated_plan)
        )
        
        meal_plan = await authenticated_client.meal_plans.update(plan_id, update_data)
        
        assert meal_plan.id == plan_id
        assert meal_plan.title == "Updated Christmas Dinner"
        assert meal_plan.recipe_id == "recipe_999"

    @pytest.mark.integration
    async def test_delete_meal_plan_success(self, integration_httpx_mock, authenticated_client):
        """Test successful meal plan deletion."""
        plan_id = "delete-plan-101"
        integration_httpx_mock.delete(f"/api/households/mealplans/{plan_id}").mock(
            return_value=httpx.Response(204)
        )
        
        result = await authenticated_client.meal_plans.delete(plan_id)
        assert result is True

    @pytest.mark.integration
    async def test_delete_meal_plan_not_found(self, integration_httpx_mock, authenticated_client):
        """Test deletion of non-existent meal plan."""
        plan_id = "nonexistent-plan"
        integration_httpx_mock.delete(f"/api/households/mealplans/{plan_id}").mock(
            return_value=httpx.Response(404, json={"detail": "Meal plan not found"})
        )
        
        with pytest.raises(NotFoundError):
            await authenticated_client.meal_plans.delete(plan_id)


class TestMealPlansDateFiltering:
    """Test suite for meal plan date filtering functionality."""

    @pytest.mark.integration
    async def test_get_meal_plans_single_date(self, integration_httpx_mock, authenticated_client):
        """Test fetching meal plans for a single date."""
        target_date = date(2023, 12, 25)
        
        plans_for_date = [
            {
                "id": "christmas_breakfast",
                "date": "2023-12-25",
                "entry_type": "breakfast",
                "title": "Christmas Breakfast"
            },
            {
                "id": "christmas_dinner",
                "date": "2023-12-25",
                "entry_type": "dinner",
                "title": "Christmas Dinner"
            }
        ]
        
        integration_httpx_mock.get("/api/households/mealplans").mock(
            return_value=httpx.Response(200, json=plans_for_date)
        )
        
        meal_plans = await authenticated_client.meal_plans.get_all(
            start_date=target_date,
            end_date=target_date
        )
        
        assert len(meal_plans) == 2
        assert all(str(plan.date) == "2023-12-25" for plan in meal_plans)

    @pytest.mark.integration
    async def test_get_meal_plans_week_range(self, integration_httpx_mock, authenticated_client):
        """Test fetching meal plans for a week range."""
        start_date = date(2023, 12, 25)  # Monday
        end_date = date(2023, 12, 31)    # Sunday
        
        week_plans = [
            {
                "id": f"plan_day_{i}",
                "date": f"2023-12-{25 + i}",
                "entry_type": "dinner",
                "title": f"Day {i + 1} Dinner"
            }
            for i in range(7)  # 7 days
        ]
        
        integration_httpx_mock.get("/api/households/mealplans").mock(
            return_value=httpx.Response(200, json=week_plans)
        )
        
        meal_plans = await authenticated_client.meal_plans.get_all(
            start_date=start_date,
            end_date=end_date
        )
        
        assert len(meal_plans) == 7

    @pytest.mark.integration
    async def test_get_meal_plans_no_date_filter(self, integration_httpx_mock, authenticated_client):
        """Test fetching all meal plans without date filtering."""
        all_plans = [
            {
                "id": "plan_past",
                "date": "2023-11-01",
                "entry_type": "dinner",
                "title": "Past Dinner"
            },
            {
                "id": "plan_future",
                "date": "2024-01-01",
                "entry_type": "dinner",
                "title": "Future Dinner"
            }
        ]
        
        integration_httpx_mock.get("/api/households/mealplans").mock(
            return_value=httpx.Response(200, json=all_plans)
        )
        
        meal_plans = await authenticated_client.meal_plans.get_all()
        
        assert len(meal_plans) == 2

    @pytest.mark.integration
    async def test_get_meal_plans_future_only(self, integration_httpx_mock, authenticated_client):
        """Test fetching only future meal plans."""
        future_date = date.today() + timedelta(days=30)
        
        future_plans = [
            {
                "id": "future_plan",
                "date": future_date.isoformat(),
                "entry_type": "dinner",
                "title": "Future Dinner"
            }
        ]
        
        integration_httpx_mock.get("/api/households/mealplans").mock(
            return_value=httpx.Response(200, json=future_plans)
        )
        
        meal_plans = await authenticated_client.meal_plans.get_all(start_date=future_date)
        
        assert len(meal_plans) == 1
        assert meal_plans[0].title == "Future Dinner"


class TestMealPlansValidation:
    """Test suite for meal plan validation scenarios."""

    @pytest.mark.integration
    async def test_create_meal_plan_invalid_date(self, integration_httpx_mock, authenticated_client):
        """Test creating meal plan with invalid date format."""
        integration_httpx_mock.post("/api/households/mealplans").mock(
            return_value=httpx.Response(422, json={
                "detail": [
                    {"loc": ["date"], "msg": "invalid date format", "type": "value_error.date"}
                ]
            })
        )
        
        plan_data = {
            "date": "invalid-date",
            "entry_type": "dinner",
            "title": "Invalid Date Plan"
        }
        
        with pytest.raises(ValidationError):
            await authenticated_client.meal_plans.create(plan_data)

    @pytest.mark.integration
    async def test_create_meal_plan_invalid_entry_type(self, integration_httpx_mock, authenticated_client):
        """Test creating meal plan with invalid entry type."""
        integration_httpx_mock.post("/api/households/mealplans").mock(
            return_value=httpx.Response(422, json={
                "detail": [
                    {"loc": ["entry_type"], "msg": "must be one of: breakfast, lunch, dinner, snack", "type": "value_error"}
                ]
            })
        )
        
        plan_data = {
            "date": "2023-12-25",
            "entry_type": "invalid_type",
            "title": "Invalid Entry Type Plan"
        }
        
        with pytest.raises(ValidationError):
            await authenticated_client.meal_plans.create(plan_data)

    @pytest.mark.integration
    async def test_create_meal_plan_nonexistent_recipe(self, integration_httpx_mock, authenticated_client):
        """Test creating meal plan with non-existent recipe."""
        integration_httpx_mock.post("/api/households/mealplans").mock(
            return_value=httpx.Response(422, json={
                "detail": [
                    {"loc": ["recipe_id"], "msg": "recipe not found", "type": "value_error"}
                ]
            })
        )
        
        plan_data = {
            "date": "2023-12-25",
            "entry_type": "dinner",
            "title": "Plan with Invalid Recipe",
            "recipe_id": "nonexistent_recipe"
        }
        
        with pytest.raises(ValidationError):
            await authenticated_client.meal_plans.create(plan_data)

    @pytest.mark.integration
    async def test_update_meal_plan_past_date_restriction(self, integration_httpx_mock, authenticated_client):
        """Test updating meal plan for past dates (if restricted)."""
        plan_id = "past-plan"
        integration_httpx_mock.put(f"/api/households/mealplans/{plan_id}").mock(
            return_value=httpx.Response(422, json={
                "detail": "Cannot modify meal plans for past dates"
            })
        )
        
        update_data = {
            "title": "Updated Past Plan"
        }
        
        with pytest.raises(ValidationError):
            await authenticated_client.meal_plans.update(plan_id, update_data)


class TestMealPlansWorkflows:
    """Test suite for complex meal planning workflows."""

    @pytest.mark.integration
    async def test_weekly_meal_planning_workflow(self, integration_httpx_mock, authenticated_client):
        """Test complete weekly meal planning workflow."""
        # Create meal plans for a week
        week_start = date(2023, 12, 25)
        plans_to_create = []
        created_plans = []
        
        for i in range(7):
            plan_date = week_start + timedelta(days=i)
            plan_data = {
                "date": plan_date.isoformat(),
                "entry_type": "dinner",
                "title": f"Week Day {i + 1} Dinner",
                "recipe_id": f"recipe_{i + 1}"
            }
            plans_to_create.append(plan_data)
            
            created_plan = {
                "id": f"week_plan_{i + 1}",
                **plan_data,
                "created_at": "2023-12-01T00:00:00Z"
            }
            created_plans.append(created_plan)
            
            # Mock creation for each plan
            integration_httpx_mock.post("/api/households/mealplans").mock(
                return_value=httpx.Response(201, json=created_plan)
            )
        
        # Mock fetching the week's plans
        integration_httpx_mock.get("/api/households/mealplans").mock(
            return_value=httpx.Response(200, json=created_plans)
        )
        
        # Execute workflow
        # 1. Create plans for the week
        created_meal_plans = []
        for plan_data in plans_to_create:
            plan = await authenticated_client.meal_plans.create(plan_data)
            created_meal_plans.append(plan)
        
        assert len(created_meal_plans) == 7
        
        # 2. Fetch the week's meal plans
        week_plans = await authenticated_client.meal_plans.get_all(
            start_date=week_start,
            end_date=week_start + timedelta(days=6)
        )
        
        assert len(week_plans) == 7

    @pytest.mark.integration
    async def test_meal_plan_recipe_replacement_workflow(self, integration_httpx_mock, authenticated_client):
        """Test replacing recipe in existing meal plan."""
        plan_id = "replaceable-plan"
        
        # Mock get existing plan
        existing_plan = {
            "id": plan_id,
            "date": "2023-12-25",
            "entry_type": "dinner",
            "title": "Christmas Dinner",
            "recipe_id": "old_recipe"
        }
        
        integration_httpx_mock.get(f"/api/households/mealplans/{plan_id}").mock(
            return_value=httpx.Response(200, json=existing_plan)
        )
        
        # Mock update with new recipe
        updated_plan = {
            **existing_plan,
            "recipe_id": "new_recipe",
            "title": "Updated Christmas Dinner",
            "updated_at": "2023-12-01T12:00:00Z"
        }
        
        integration_httpx_mock.put(f"/api/households/mealplans/{plan_id}").mock(
            return_value=httpx.Response(200, json=updated_plan)
        )
        
        # Execute workflow
        # 1. Get existing plan
        plan = await authenticated_client.meal_plans.get(plan_id)
        assert plan.recipe_id == "old_recipe"
        
        # 2. Update with new recipe
        updated = await authenticated_client.meal_plans.update(
            plan_id,
            {
                "recipe_id": "new_recipe",
                "title": "Updated Christmas Dinner"
            }
        )
        
        assert updated.recipe_id == "new_recipe"
        assert updated.title == "Updated Christmas Dinner"

    @pytest.mark.integration
    async def test_meal_plan_batch_operations(self, integration_httpx_mock, authenticated_client):
        """Test batch meal plan operations."""
        # Create multiple meal plans
        plans_data = [
            {
                "date": f"2023-12-{25 + i}",
                "entry_type": "dinner",
                "title": f"Batch Plan {i + 1}"
            }
            for i in range(3)
        ]
        
        created_plans = []
        for i, plan_data in enumerate(plans_data):
            created_plan = {
                "id": f"batch_plan_{i + 1}",
                **plan_data,
                "created_at": "2023-12-01T00:00:00Z"
            }
            created_plans.append(created_plan)
            
            integration_httpx_mock.post("/api/households/mealplans").mock(
                return_value=httpx.Response(201, json=created_plan)
            )
        
        # Create plans in batch
        results = []
        for plan_data in plans_data:
            plan = await authenticated_client.meal_plans.create(plan_data)
            results.append(plan)
        
        assert len(results) == 3
        assert all(plan.title.startswith("Batch Plan") for plan in results)

    @pytest.mark.integration
    async def test_meal_plan_with_recipe_details_workflow(self, integration_httpx_mock, authenticated_client):
        """Test meal plan workflow with detailed recipe information."""
        plan_id = "detailed-recipe-plan"
        
        # Mock meal plan with full recipe details
        detailed_plan = {
            "id": plan_id,
            "date": "2023-12-25",
            "entry_type": "dinner",
            "title": "Christmas Feast",
            "recipe_id": "turkey_recipe",
            "recipe": {
                "id": "turkey_recipe",
                "name": "Roast Turkey with Herbs",
                "slug": "roast-turkey-herbs",
                "description": "Perfect holiday turkey",
                "prep_time": "PT30M",
                "cook_time": "PT3H",
                "total_time": "PT3H30M",
                "recipe_yield": "8 servings",
                "image": "turkey.jpg",
                "recipe_category": [{"name": "Main Course"}],
                "tags": [{"name": "Holiday"}, {"name": "Special Occasion"}]
            }
        }
        
        integration_httpx_mock.get(f"/api/households/mealplans/{plan_id}").mock(
            return_value=httpx.Response(200, json=detailed_plan)
        )
        
        # Execute workflow
        plan = await authenticated_client.meal_plans.get(plan_id)
        
        assert plan.title == "Christmas Feast"
        assert hasattr(plan, 'recipe')
        assert plan.recipe is not None 