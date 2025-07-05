"""
Meal plan models for the Mealie SDK.

This module contains data models for meal plans, meal planning, and meal scheduling.
"""

from datetime import date
from typing import Any, Dict, Optional, Union

from .common import BaseModel, MealPlanType, convert_date, QueryFilter, OrderDirection, OrderByNullPosition

class MealPlan(BaseModel):
    """Complete meal plan with entries for multiple dates."""

    def __init__(
        self,
        id: Optional[str] = None,
        group_id: Optional[str] = None,
        user_id: Optional[str] = None,
        household_id: Optional[str] = None,
        recipe_id: Optional[str] = None,
        date: Optional[Union[str, date]] = None,
        entry_type: Optional[MealPlanType] = None,
        title: Optional[str] = None,
        text: Optional[str] = None,
        recipe: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> None:
        self.id = id
        self.group_id = group_id
        self.user_id = user_id
        self.household_id = household_id
        self.recipe_id = recipe_id
        self.date = convert_date(date)
        self.entry_type = entry_type
        self.title = title
        self.text = text
        self.recipe = recipe
        super().__init__(**kwargs)

class MealPlanCreateRequest(BaseModel):
    """Request model for creating a new meal plan."""

    def __init__(
        self,
        date: Union[str, date],
        entry_type: MealPlanType = MealPlanType.DINNER,
        title: Optional[str] = None,
        text: Optional[str] = None,
        recipe_id: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        self.date = convert_date(date)
        self.entry_type = entry_type
        self.title = title
        self.text = text
        self.recipe_id = recipe_id
        super().__init__(**kwargs)


class MealPlanUpdateRequest(BaseModel):
    """Request model for updating meal plan information."""

    def __init__(
        self,
        date: Optional[Union[str, date]] = None,
        entry_type: Optional[MealPlanType] = None,
        title: Optional[str] = None,
        text: Optional[str] = None,
        recipe_id: Optional[str] = None,
        id: Optional[str] = None,
        group_id: Optional[str] = None,
        user_id: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        self.id = id
        self.group_id = group_id
        self.user_id = user_id
        self.date = convert_date(date) if date else None
        self.entry_type = entry_type
        self.title = title
        self.text = text
        self.recipe_id = recipe_id
        super().__init__(**kwargs)

class MealPlanSummary(BaseModel):
    """Summary of a meal plan."""
    
    def __init__(
        self,
        id: Optional[str] = None,
        date: Optional[Union[str, date]] = None,
        entry_type: Optional[MealPlanType] = None,
        household_id: Optional[str] = None,
        group_id: Optional[str] = None,
        recipe_id: Optional[str] = None,
        title: Optional[str] = None,
        text: Optional[str] = None,
        user_id: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        self.id = id
        self.date = convert_date(date) if date else None
        self.entry_type = entry_type
        self.household_id = household_id
        self.group_id = group_id
        self.recipe_id = recipe_id
        self.title = title
        self.text = text
        self.user_id = user_id
        super().__init__(**kwargs)


class MealPlanFilter(QueryFilter):
    """Filter options for meal plan queries."""

    def __init__(
        self,
        start_date: Optional[Union[str, date]] = None,
        end_date: Optional[Union[str, date]] = None,
        page: int = 1,
        per_page: int = 50,
        order_by: Optional[str] = None,
        order_direction: OrderDirection = OrderDirection.ASC,
        order_by_null_position: OrderByNullPosition = OrderByNullPosition.LAST,
        accept_language: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            page=page,
            per_page=per_page,
            order_by=order_by,
            order_direction=order_direction,
            order_by_null_position=order_by_null_position,
            accept_language=accept_language,
            **kwargs)
        self.start_date = convert_date(start_date) if start_date else None
        self.end_date = convert_date(end_date) if end_date else None

    def to_params(self) -> Dict[str, Any]:
        """Convert filter to query parameters."""
        params = super().to_params()
        
        if self.start_date:
            params["start_date"] = self.start_date.isoformat()
            
        if self.end_date:
            params["end_date"] = self.end_date.isoformat()
            
        return params 