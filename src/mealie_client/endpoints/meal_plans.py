"""
Meal plans endpoint manager for the Mealie SDK.
"""

from typing import Any, Dict, List, Union
from datetime import date

from ..models.meal_plan import (
    MealPlan,
    MealPlanCreateRequest,
    MealPlanSummary,
    MealPlanUpdateRequest,
    MealPlanFilter,
)
from ..models.common import OrderDirection, OrderByNullPosition
from ..exceptions import NotFoundError


class MealPlansManager:
    """Manages meal plan-related API operations."""

    def __init__(self, client: Any) -> None:
        self.client = client

    async def get_all(
        self,
        start_date: date | None = None,
        end_date: date | None = None,
        order_by: str | None = None,
        order_direction: OrderDirection = OrderDirection.ASC,
        order_by_null_position: OrderByNullPosition = OrderByNullPosition.LAST,
        page: int = 1,
        per_page: int = 50,
        accept_language: str | None = None,
    ) -> List[MealPlanSummary]:
        """Get all meal plans with optional date filtering."""
        response = await self.client.get(
            "households/mealplans",
            params=MealPlanFilter(
                start_date=start_date,
                end_date=end_date,
                order_by=order_by,
                order_direction=order_direction,
                order_by_null_position=order_by_null_position,
                page=page,
                per_page=per_page,
                accept_language=accept_language,
            ).to_params(),
        )
        if isinstance(response, list):
            plans_data = response
        elif isinstance(response, dict) and "items" in response:
            plans_data = response["items"]
        else:
            plans_data = []

        return [
            MealPlanSummary.from_dict(plan_data) if isinstance(plan_data, dict) else plan_data
            for plan_data in plans_data
        ]

    async def get(self, plan_id: str, accept_language: str | None = None) -> MealPlan:
        """Get a specific meal plan by ID."""
        try:
            response = await self.client.get(
                f"households/mealplans/{plan_id}",
                params=MealPlanFilter(
                    accept_language=accept_language,
                ).to_params(),
            )
            return (
                MealPlan.from_dict(response) if isinstance(response, dict) else response
            )
        except Exception as e:
            if hasattr(e, "status_code") and getattr(e, "status_code") == 404:
                raise NotFoundError(
                    f"Meal plan '{plan_id}' not found",
                    resource_type="meal_plan",
                    resource_id=plan_id,
                )
            raise

    async def get_today(self, accept_language: str | None = None) -> MealPlan:
        """Get the current user's meal plan for today."""
        response = await self.client.get(
            "households/mealplans/today",
            params=MealPlanFilter(
                accept_language=accept_language,
            ).to_params(),
        )
        return MealPlan.from_dict(response) if isinstance(response, dict) else response

    async def create(
        self, plan_data: MealPlanCreateRequest, accept_language: str | None = None
    ) -> MealPlan:
        """Create a new meal plan."""
        if isinstance(plan_data, MealPlanCreateRequest):
            data = plan_data.to_dict()
        else:
            data = plan_data

        response = await self.client.post(
            "households/mealplans",
            json_data=data,
            params=MealPlanFilter(
                accept_language=accept_language,
            ).to_params(),
        )
        return MealPlan.from_dict(response) if isinstance(response, dict) else response

    async def update(
        self,
        plan_id: str,
        plan_data: MealPlanUpdateRequest,
        accept_language: str | None = None,
    ) -> MealPlan:
        """Update an existing meal plan."""
        if isinstance(plan_data, MealPlanUpdateRequest):
            data = plan_data.to_dict()
        else:
            data = plan_data

        try:
            response = await self.client.put(
                f"households/mealplans/{plan_id}", json_data={
                    **data,
                    "id": plan_id,
                },
                params=MealPlanFilter(
                    accept_language=accept_language,
                ).to_params(),
            )
            return (
                MealPlan.from_dict(response) if isinstance(response, dict) else response
            )
        except Exception as e:
            if hasattr(e, "status_code") and getattr(e, "status_code") == 404:
                raise NotFoundError(
                    f"Meal plan '{plan_id}' not found",
                    resource_type="meal_plan",
                    resource_id=plan_id,
                )
            raise

    async def delete(self, plan_id: str, accept_language: str | None = None) -> bool:
        """Delete a meal plan."""
        try:
            await self.client.delete(
                f"households/mealplans/{plan_id}",
                params=MealPlanFilter(
                    accept_language=accept_language,
                ).to_params(),
            )
            return True
        except Exception as e:
            if hasattr(e, "status_code") and getattr(e, "status_code") == 404:
                raise NotFoundError(
                    f"Meal plan '{plan_id}' not found",
                    resource_type="meal_plan",
                    resource_id=plan_id,
                )
            raise
