"""
Group models for the Mealie SDK.

This module contains data models for groups and group management.
"""

from typing import Any, Dict, List, Optional

from .common import BaseModel, QueryFilter, OrderDirection, OrderByNullPosition 

class HouseHoldPreferences(BaseModel):
    """Preferences for a household."""
    
    def __init__(
        self,
        id: Optional[str] = None,
        privateHousehold: bool = True,
        lockRecipeEditsFromOtherHouseholds: bool = True,
        firstDayOfWeek: int = 0,
        recipePublic: bool = True,
        recipeShowNutrition: bool = False,
        recipeShowAssets: bool = False,
        recipeLandscapeView: bool = False,
        recipeDisableComments: bool = False,
        recipeDisableAmount: bool = True,
        **kwargs: Any,
    ) -> None:
        self.id = id
        self.privateHousehold = privateHousehold
        self.lockRecipeEditsFromOtherHouseholds = lockRecipeEditsFromOtherHouseholds
        self.firstDayOfWeek = firstDayOfWeek
        self.recipePublic = recipePublic
        self.recipeShowNutrition = recipeShowNutrition
        self.recipeShowAssets = recipeShowAssets
        self.recipeLandscapeView = recipeLandscapeView
        self.recipeDisableComments = recipeDisableComments
        self.recipeDisableAmount = recipeDisableAmount
        super().__init__(**kwargs)

class Household(BaseModel):
    """Complete household model with settings and preferences."""

    def __init__(
        self,
        id: Optional[str] = None,
        name: str = "",
        slug: Optional[str] = None,
        group_id: Optional[str] = None,
        preferences: Optional[HouseHoldPreferences] = None,
        group: Optional[str] = None,
        users: Optional[List[Dict[str, Any]]] = None,
        webhooks: Optional[List[Dict[str, Any]]] = None,
        **kwargs: Any,
    ) -> None:
        self.id = id
        self.name = name
        self.slug = slug
        self.group_id = group_id
        self.preferences = preferences or HouseHoldPreferences()
        self.group = group
        self.users = users
        self.webhooks = webhooks
        super().__init__(**kwargs)


class HouseholdCreateRequest(BaseModel):
    """Request model for creating a new household."""

    def __init__(
        self,
        group_id: str,
        name: str,
        **kwargs: Any,
    ) -> None:
        self.group_id = group_id
        self.name = name
        super().__init__(**kwargs)


class HouseholdUpdateRequest(BaseModel):
    """Request model for updating household information."""

    def __init__(
        self,
        id: Optional[str] = None,
        group_id: Optional[str] = None,
        name: Optional[str] = None,
        preferences: Optional[HouseHoldPreferences] = None,
        **kwargs: Any,
    ) -> None:
        self.id = id
        self.group_id = group_id
        self.name = name
        self.preferences = preferences or HouseHoldPreferences()
        super().__init__(**kwargs)


class HouseholdSummary(BaseModel):
    """Lightweight household summary for list views."""

    def __init__(
        self,
        id: Optional[str] = None,
        name: str = "",
        slug: Optional[str] = None,
        group_id: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        self.id = id
        self.name = name
        self.slug = slug
        self.group_id = group_id
        super().__init__(**kwargs) 

class HouseholdFilter(QueryFilter):
    """Filter for households."""

    def __init__(
        self,
        page: int = 1,
        per_page: int = 50,
        order_by: Optional[str] = None,
        order_direction: OrderDirection = OrderDirection.ASC,
        order_by_null_position: OrderByNullPosition = OrderByNullPosition.LAST,
        search: Optional[str] = None,
        accept_language: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            page=page,
            per_page=per_page,
            order_by=order_by,
            order_direction=order_direction,
            order_by_null_position=order_by_null_position,
            search=search,
            accept_language=accept_language,
            **kwargs,
        )