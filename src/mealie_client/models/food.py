"""
Food models for the Mealie SDK.

This module contains data models for food and food management.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from .common import BaseModel, OrderByNullPosition, OrderDirection, QueryFilter, convert_datetime


class Food(BaseModel):
    """Complete food model with settings and preferences."""

    def __init__(
        self,
        id: Optional[str] = None,
        name: str = "",
        pluralName: str = "",
        description: str = "",
        extras: Optional[Dict[str, Any]] = None,
        labelId: Optional[str] = None,
        aliases: Optional[List[str]] = None,
        householdsWithIngredientFood: Optional[List[str]] = None,
        label: Optional[Dict[str, Any]] = None,
        createdAt: Optional[Union[str, datetime]] = None,
        updatedAt: Optional[Union[str, datetime]] = None,
        **kwargs: Any,
    ) -> None:
        self.id = id
        self.name = name
        self.pluralName = pluralName
        self.description = description
        self.extras = extras or {}
        self.labelId = labelId
        self.aliases = aliases or []
        self.householdsWithIngredientFood = householdsWithIngredientFood or []
        self.label = label
        self.createdAt = convert_datetime(createdAt)
        self.updatedAt = convert_datetime(updatedAt)
        super().__init__(**kwargs)


class FoodCreateRequest(BaseModel):
    """Request model for creating a new group."""

    def __init__(
        self,
        name: str,
        pluralName: str,
        id: Optional[str] = None,
        description: Optional[str] = None,
        extras: Optional[Dict[str, Any]] = None,
        labelId: Optional[str] = None,
        aliases: Optional[List[str]] = None,
        householdsWithIngredientFood: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> None:
        self.name = name
        self.pluralName = pluralName
        self.description = description
        self.extras = extras or {}
        self.labelId = labelId
        self.aliases = aliases or []
        self.householdsWithIngredientFood = householdsWithIngredientFood or []
        super().__init__(**kwargs)


class FoodUpdateRequest(BaseModel):
    """Request model for updating food information."""

    def __init__(
        self,
        name: Optional[str] = None,
        pluralName: Optional[str] = None,
        description: Optional[str] = None,
        extras: Optional[Dict[str, Any]] = None,
        labelId: Optional[str] = None,
        aliases: Optional[List[str]] = None,
        householdsWithIngredientFood: Optional[List[str]] = None,
        label: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> None:
        self.name = name
        self.pluralName = pluralName
        self.description = description
        self.extras = extras or {}
        self.labelId = labelId
        self.aliases = aliases or []
        self.householdsWithIngredientFood = householdsWithIngredientFood or []
        self.label = label
        super().__init__(**kwargs)


class FoodSummary(BaseModel):
    """Lightweight food summary for list views."""

    def __init__(
        self,
        id: Optional[str] = None,
        name: str = "",
        pluralName: str = "",
        description: str = "",
        extras: Optional[Dict[str, Any]] = None,
        labelId: Optional[str] = None,
        aliases: Optional[List[str]] = None,
        householdsWithIngredientFood: Optional[List[str]] = None,
        label: Optional[Dict[str, Any]] = None,
        createdAt: Optional[Union[str, datetime]] = None,
        updatedAt: Optional[Union[str, datetime]] = None,
        **kwargs: Any,
    ) -> None:
        self.id = id
        self.name = name
        self.pluralName = pluralName
        self.description = description
        self.extras = extras or {}
        self.labelId = labelId
        self.aliases = aliases or []
        self.householdsWithIngredientFood = householdsWithIngredientFood or []
        self.label = label
        self.createdAt = convert_datetime(createdAt)
        self.updatedAt = convert_datetime(updatedAt)
        super().__init__(**kwargs) 

class FoodFilter(QueryFilter):
    """Filter for food queries."""

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