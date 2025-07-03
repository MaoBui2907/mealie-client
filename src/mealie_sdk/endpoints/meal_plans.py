"""
Meal plans endpoint manager for the Mealie SDK.
"""

from typing import Any, Dict, List, Union
from datetime import date

from ..models.meal_plan import MealPlan, MealPlanCreateRequest, MealPlanUpdateRequest, MealPlanFilter
from ..exceptions import NotFoundError


class MealPlansManager:
    """Manages meal plan-related API operations."""

    def __init__(self, client: Any) -> None:
        self.client = client

    async def get_all(self, start_date: date = None, end_date: date = None) -> List[MealPlan]:
        """Get all meal plans with optional date filtering."""
        params = {}
        if start_date:
            params["start_date"] = start_date.isoformat()
        if end_date:
            params["end_date"] = end_date.isoformat()
            
        response = await self.client.get("groups/mealplans", params=params)
        
        if isinstance(response, list):
            plans_data = response
        elif isinstance(response, dict) and "items" in response:
            plans_data = response["items"]
        else:
            plans_data = []

        return [
            MealPlan.from_dict(plan_data) if isinstance(plan_data, dict) else plan_data
            for plan_data in plans_data
        ]

    async def get(self, plan_id: str) -> MealPlan:
        """Get a specific meal plan by ID."""
        try:
            response = await self.client.get(f"groups/mealplans/{plan_id}")
            return MealPlan.from_dict(response) if isinstance(response, dict) else response
        except Exception as e:
            if hasattr(e, 'status_code') and e.status_code == 404:
                raise NotFoundError(
                    f"Meal plan '{plan_id}' not found",
                    resource_type="meal_plan",
                    resource_id=plan_id,
                )
            raise

    async def create(self, plan_data: Union[MealPlanCreateRequest, Dict[str, Any]]) -> MealPlan:
        """Create a new meal plan."""
        if isinstance(plan_data, MealPlanCreateRequest):
            data = plan_data.to_dict()
        else:
            data = plan_data

        response = await self.client.post("groups/mealplans", json_data=data)
        return MealPlan.from_dict(response) if isinstance(response, dict) else response

    async def update(
        self,
        plan_id: str,
        plan_data: Union[MealPlanUpdateRequest, Dict[str, Any]],
    ) -> MealPlan:
        """Update an existing meal plan."""
        if isinstance(plan_data, MealPlanUpdateRequest):
            data = plan_data.to_dict()
        else:
            data = plan_data

        try:
            response = await self.client.put(f"groups/mealplans/{plan_id}", json_data=data)
            return MealPlan.from_dict(response) if isinstance(response, dict) else response
        except Exception as e:
            if hasattr(e, 'status_code') and e.status_code == 404:
                raise NotFoundError(
                    f"Meal plan '{plan_id}' not found",
                    resource_type="meal_plan",
                    resource_id=plan_id,
                )
            raise

    async def delete(self, plan_id: str) -> bool:
        """Delete a meal plan."""
        try:
            await self.client.delete(f"groups/mealplans/{plan_id}")
            return True
        except Exception as e:
            if hasattr(e, 'status_code') and e.status_code == 404:
                raise NotFoundError(
                    f"Meal plan '{plan_id}' not found",
                    resource_type="meal_plan",
                    resource_id=plan_id,
                )
            raise 