"""
Unit tests for meal plan models.

Tests cover all meal plan model classes, methods, serialization,
and data conversion functionality.
"""

from datetime import datetime, date, timedelta
from unittest.mock import patch
from uuid import uuid4

import pytest

from mealie_client.models.meal_plan import (
    MealPlan,
    MealPlanCreateRequest,
    MealPlanUpdateRequest,
    MealPlanFilter,
)
from mealie_client.models.common import MealPlanType

class TestMealPlan:
    """Test suite for MealPlan model."""

    @pytest.mark.unit
    def test_init_minimal(self):
        """Test MealPlan initialization with minimal data."""
        plan = MealPlan()
        
        assert plan.id is None
        assert plan.group_id is None
        assert plan.user_id is None

    @pytest.mark.unit
    def test_from_dict_no_entries(self):
        """Test creating MealPlan from dict without entries."""
        data = {"id": "plan-123"}
        plan = MealPlan.from_dict(data)
        
        assert plan.id == "plan-123"

    @pytest.mark.unit
    def test_equality(self):
        """Test MealPlan equality comparison."""
        plan1 = MealPlan(
            id="plan-123",
            start_date="2023-12-01",
            end_date="2023-12-07",
        )
        plan2 = MealPlan(
            id="plan-123",
            start_date="2023-12-01",
            end_date="2023-12-07",
        )
        plan3 = MealPlan(
            id="plan-456",
            start_date="2023-12-01",
            end_date="2023-12-07",
        )
        
        assert plan1 == plan2
        assert plan1 != plan3
        assert plan1 != "not a plan"


class TestMealPlanCreateRequest:
    """Test suite for MealPlanCreateRequest model."""

    @pytest.mark.unit
    def test_init_minimal(self):
        """Test MealPlanCreateRequest initialization with minimal data."""
        request = MealPlanCreateRequest(
            date=date(2023, 12, 1),
            entry_type=MealPlanType.BREAKFAST,  
            title="Morning",
            recipe_id="recipe-1",
        )
        
        assert request.date == date(2023, 12, 1)
        assert request.entry_type == MealPlanType.BREAKFAST
        assert request.title == "Morning"
        assert request.recipe_id == "recipe-1"

    @pytest.mark.unit
    def test_init_with_entries(self):
        """Test MealPlanCreateRequest initialization with entries."""
        request = MealPlanCreateRequest(
            date=date(2023, 12, 1),
            entry_type=MealPlanType.BREAKFAST,
            title="Morning",
            recipe_id="recipe-1",
        )
        
        assert request.date == date(2023, 12, 1)
        assert request.entry_type == MealPlanType.BREAKFAST
        assert request.title == "Morning"
        assert request.recipe_id == "recipe-1"

    @pytest.mark.unit
    def test_to_dict(self):
        """Test converting MealPlanCreateRequest to dictionary."""
        request = MealPlanCreateRequest(
            date=date(2023, 12, 1),
            entry_type=MealPlanType.BREAKFAST,
            title="Morning",
            recipe_id="recipe-1",
        )
        
        result = request.to_dict()
        
        assert result["date"] == "2023-12-01"
        assert result["entryType"] == "breakfast"
        assert result["title"] == "Morning"
        assert result["recipeId"] == "recipe-1"


class TestMealPlanUpdateRequest:
    """Test suite for MealPlanUpdateRequest model."""

    @pytest.mark.unit
    def test_init_minimal(self):
        """Test MealPlanUpdateRequest initialization with minimal data."""
        request = MealPlanUpdateRequest()
        
        assert request.id is None
        assert request.group_id is None
        assert request.user_id is None
        assert request.date is None
        assert request.entry_type is None
        assert request.title is None
        assert request.text is None
        assert request.recipe_id is None

    @pytest.mark.unit
    def test_init_partial_update(self):
        """Test MealPlanUpdateRequest initialization with partial data."""
        request = MealPlanUpdateRequest(
            date=date(2023, 12, 14),
            entry_type=MealPlanType.BREAKFAST,
            title="Morning",
            recipe_id="recipe-1",
        )
        
        assert request.date == date(2023, 12, 14)
        assert request.entry_type == MealPlanType.BREAKFAST
        assert request.title == "Morning"
        assert request.recipe_id == "recipe-1"

class TestMealPlanFilter:
    """Test suite for MealPlanFilter model."""

    @pytest.mark.unit
    def test_init_minimal(self):
        """Test MealPlanFilter initialization with default values."""
        filter_obj = MealPlanFilter()
        
        assert filter_obj.start_date is None
        assert filter_obj.end_date is None
        assert filter_obj.page == 1
        assert filter_obj.per_page == 50

    @pytest.mark.unit
    def test_init_full(self):
        """Test MealPlanFilter initialization with all data."""
        filter_obj = MealPlanFilter(
            start_date="2023-12-01",
            end_date=date(2023, 12, 31),
            page=2,
            per_page=25,
        )
        
        assert filter_obj.start_date == date(2023, 12, 1)
        assert filter_obj.end_date == date(2023, 12, 31)
        assert filter_obj.page == 2
        assert filter_obj.per_page == 25

    @pytest.mark.unit
    def test_to_params_minimal(self):
        """Test converting MealPlanFilter to params with minimal data."""
        filter_obj = MealPlanFilter()
        params = filter_obj.to_params()
        
        expected = {
            "page": 1,
            "perPage": 50,
            "orderByNullPosition": "last",
        }
        assert params == expected

    @pytest.mark.unit
    def test_to_dict(self):
        """Test converting MealPlanFilter to dictionary."""
        filter_obj = MealPlanFilter(
            start_date="2023-12-01",
            end_date="2023-12-31",
            page=2,
            per_page=25,
        )
        
        result = filter_obj.to_dict()
        
        assert result["start_date"] == "2023-12-01"
        assert result["end_date"] == "2023-12-31"
        assert result["page"] == 2
        assert result["per_page"] == 25


class TestMealPlanEdgeCases:
    """Test suite for edge cases and error scenarios."""

    @pytest.mark.unit
    def test_meal_plan_invalid_dates(self):
        """Test MealPlan with invalid date formats."""
        with patch('mealie_client.models.common.convert_date') as mock_convert_date, \
             patch('mealie_client.models.common.convert_datetime') as mock_convert_datetime:
            mock_convert_date.return_value = None
            mock_convert_datetime.return_value = None
            
            plan = MealPlan(
                start_date="invalid",
                end_date="invalid",
                created_at="invalid",
                updated_at="invalid",
            )
            
            assert plan.date is None