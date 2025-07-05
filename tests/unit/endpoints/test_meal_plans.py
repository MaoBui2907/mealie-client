"""
Unit tests for MealPlansManager endpoint.

Tests cover meal plan operations including CRUD operations.
"""

from unittest.mock import AsyncMock
from uuid import uuid4
from datetime import UTC, datetime, timedelta

import pytest

from mealie_client.endpoints.meal_plans import MealPlansManager
from mealie_client.models.meal_plan import MealPlan
from mealie_client.exceptions import NotFoundError


class TestMealPlansManager:
    """Test suite for MealPlansManager class."""

    @pytest.fixture
    def meal_plans_manager(self, mealie_client):
        return MealPlansManager(mealie_client)

    @pytest.mark.unit
    def test_init(self, mealie_client):
        """Test MealPlansManager initialization."""
        manager = MealPlansManager(mealie_client)
        assert manager.client == mealie_client

    @pytest.mark.unit
    async def test_get_all(self, meal_plans_manager):
        """Test get_all meal plans."""
        mock_response = {"items": [create_test_meal_plan_data() for _ in range(3)]}
        meal_plans_manager.client.get = AsyncMock(return_value=mock_response)
        
        result = await meal_plans_manager.get_all()
        
        meal_plans_manager.client.get.assert_called_once()
        assert len(result) == 3

    # TODO: Implement this test
    @pytest.mark.skip(reason="TODO: Implement this test")
    async def test_get_by_id_success(self, meal_plans_manager):
        """Test successful get by meal plan ID."""
        plan_data = create_test_meal_plan_data()
        meal_plans_manager.client.get = AsyncMock(return_value=plan_data)
        
        result = await meal_plans_manager.get("plan-123")
        
        meal_plans_manager.client.get.assert_called_once_with("meal-plans/plan-123")
        assert isinstance(result, MealPlan)

    @pytest.mark.unit
    async def test_get_not_found_raises_error(self, meal_plans_manager):
        """Test that get raises NotFoundError for 404 responses."""
        mock_exception = Exception("Not found")
        mock_exception.status_code = 404
        meal_plans_manager.client.get = AsyncMock(side_effect=mock_exception)
        
        with pytest.raises(NotFoundError) as exc_info:
            await meal_plans_manager.get("nonexistent")
        
        assert exc_info.value.resource_type == "meal_plan"
        assert exc_info.value.resource_id == "nonexistent"

    @pytest.mark.unit
    async def test_create(self, meal_plans_manager):
        """Test meal plan creation."""
        request_data = {
            "start_date": "2023-12-01",
            "end_date": "2023-12-07",
            "group_id": "group-123"
        }
        response_data = create_test_meal_plan_data()
        meal_plans_manager.client.post = AsyncMock(return_value=response_data)
        
        result = await meal_plans_manager.create(request_data)
        
        meal_plans_manager.client.post.assert_called_once()
        assert isinstance(result, MealPlan)

    # TODO: Implement this test
    @pytest.mark.skip(reason="TODO: Implement this test")
    async def test_update(self, meal_plans_manager):
        """Test meal plan update."""
        update_data = {"end_date": "2023-12-14"}
        response_data = create_test_meal_plan_data(end_date="2023-12-14")
        meal_plans_manager.client.put = AsyncMock(return_value=response_data)
        
        result = await meal_plans_manager.update("plan-123", update_data)
        
        meal_plans_manager.client.put.assert_called_once_with("meal-plans/plan-123", json_data=update_data)
        assert isinstance(result, MealPlan)

    # TODO: Implement this test
    @pytest.mark.skip(reason="TODO: Implement this test")
    async def test_delete(self, meal_plans_manager):
        """Test meal plan deletion."""
        meal_plans_manager.client.delete = AsyncMock(return_value=None)
        
        result = await meal_plans_manager.delete("plan-123")
        
        meal_plans_manager.client.delete.assert_called_once_with("meal-plans/plan-123")
        assert result is True

    # TODO: Implement this test
    @pytest.mark.skip(reason="TODO: Implement this test")
    async def test_get_by_date_range(self, meal_plans_manager):
        """Test getting meal plans by date range."""
        mock_response = {"items": [create_test_meal_plan_data()]}
        meal_plans_manager.client.get = AsyncMock(return_value=mock_response)
        
        result = await meal_plans_manager.get_by_date_range("2023-12-01", "2023-12-31")
        
        call_args = meal_plans_manager.client.get.call_args
        params = call_args[1]["params"]
        assert params["start_date"] == "2023-12-01"
        assert params["end_date"] == "2023-12-31"


def create_test_meal_plan_data(**kwargs):
    """Create test meal plan data."""
    today = datetime.now(UTC).date()
    defaults = {
        "id": str(uuid4()),
        "group_id": "test-group",
        "user_id": "test-user",
        "start_date": today.isoformat(),
        "end_date": (today + timedelta(days=6)).isoformat(),
        "plan_rules": [],
        "shopping_list": None
    }
    defaults.update(kwargs)
    return defaults 