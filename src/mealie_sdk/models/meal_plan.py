"""
Meal plan models for the Mealie SDK.

This module contains data models for meal plans, meal planning, and meal scheduling.
"""

from datetime import datetime, date
from typing import Any, Dict, List, Optional, Union

from .common import BaseModel, MealPlanType, convert_datetime, convert_date, safe_get


class MealPlanEntry(BaseModel):
    """Single meal plan entry for a specific date and meal type."""

    def __init__(
        self,
        id: Optional[str] = None,
        date: Union[str, date] = "",
        entry_type: MealPlanType = MealPlanType.DINNER,
        title: Optional[str] = None,
        text: Optional[str] = None,
        recipe_id: Optional[str] = None,
        recipe: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> None:
        self.id = id
        self.date = convert_date(date)
        self.entry_type = entry_type
        self.title = title
        self.text = text
        self.recipe_id = recipe_id
        self.recipe = recipe
        super().__init__(**kwargs)

    def has_recipe(self) -> bool:
        """Check if this entry has an associated recipe."""
        return self.recipe_id is not None

    def get_display_title(self) -> str:
        """Get display title (recipe name if available, otherwise custom title)."""
        if self.recipe and "name" in self.recipe:
            return self.recipe["name"]
        return self.title or ""


class MealPlan(BaseModel):
    """Complete meal plan with entries for multiple dates."""

    def __init__(
        self,
        id: Optional[str] = None,
        group_id: Optional[str] = None,
        user_id: Optional[str] = None,
        start_date: Union[str, date] = "",
        end_date: Union[str, date] = "",
        entries: Optional[List[MealPlanEntry]] = None,
        created_at: Optional[Union[str, datetime]] = None,
        updated_at: Optional[Union[str, datetime]] = None,
        **kwargs: Any,
    ) -> None:
        self.id = id
        self.group_id = group_id
        self.user_id = user_id
        self.start_date = convert_date(start_date)
        self.end_date = convert_date(end_date)
        self.entries = entries or []
        self.created_at = convert_datetime(created_at)
        self.updated_at = convert_datetime(updated_at)
        super().__init__(**kwargs)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MealPlan":
        """Create a MealPlan instance from a dictionary."""
        plan_data = data.copy()
        
        # Convert entries
        if "entries" in plan_data and plan_data["entries"]:
            plan_data["entries"] = [
                MealPlanEntry.from_dict(entry) if isinstance(entry, dict) else entry
                for entry in plan_data["entries"]
            ]
        
        return cls(**plan_data)

    def get_entry_count(self) -> int:
        """Get total number of meal plan entries."""
        return len(self.entries)

    def get_recipe_count(self) -> int:
        """Get number of entries with recipes."""
        return sum(1 for entry in self.entries if entry.has_recipe())

    def get_entries_by_date(self, target_date: date) -> List[MealPlanEntry]:
        """Get all entries for a specific date."""
        return [entry for entry in self.entries if entry.date == target_date]

    def get_entries_by_type(self, meal_type: MealPlanType) -> List[MealPlanEntry]:
        """Get all entries for a specific meal type."""
        return [entry for entry in self.entries if entry.entry_type == meal_type]


class MealPlanCreateRequest(BaseModel):
    """Request model for creating a new meal plan."""

    def __init__(
        self,
        start_date: Union[str, date],
        end_date: Union[str, date],
        entries: Optional[List[Dict[str, Any]]] = None,
        **kwargs: Any,
    ) -> None:
        self.start_date = convert_date(start_date)
        self.end_date = convert_date(end_date)
        self.entries = entries or []
        super().__init__(**kwargs)


class MealPlanUpdateRequest(BaseModel):
    """Request model for updating meal plan information."""

    def __init__(
        self,
        start_date: Optional[Union[str, date]] = None,
        end_date: Optional[Union[str, date]] = None,
        entries: Optional[List[Dict[str, Any]]] = None,
        **kwargs: Any,
    ) -> None:
        self.start_date = convert_date(start_date) if start_date else None
        self.end_date = convert_date(end_date) if end_date else None
        self.entries = entries
        super().__init__(**kwargs)


class MealPlanEntryCreateRequest(BaseModel):
    """Request model for creating a meal plan entry."""

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


class MealPlanFilter(BaseModel):
    """Filter options for meal plan queries."""

    def __init__(
        self,
        start_date: Optional[Union[str, date]] = None,
        end_date: Optional[Union[str, date]] = None,
        page: int = 1,
        per_page: int = 50,
        **kwargs: Any,
    ) -> None:
        self.start_date = convert_date(start_date) if start_date else None
        self.end_date = convert_date(end_date) if end_date else None
        self.page = page
        self.per_page = per_page
        super().__init__(**kwargs)

    def to_params(self) -> Dict[str, Any]:
        """Convert filter to query parameters."""
        params = {
            "page": self.page,
            "perPage": self.per_page,
        }
        
        if self.start_date:
            params["startDate"] = self.start_date.isoformat()
            
        if self.end_date:
            params["endDate"] = self.end_date.isoformat()
            
        return params 