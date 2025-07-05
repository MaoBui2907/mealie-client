"""
Group models for the Mealie SDK.

This module contains data models for groups and group management.
"""

from typing import Any, Dict, List, Optional

from .common import BaseModel, OrderByNullPosition, OrderDirection, QueryFilter


class Group(BaseModel):
    """Complete group model with settings and preferences."""

    def __init__(
        self,
        id: Optional[str] = None,
        name: str = "",
        slug: Optional[str] = None,
        categories: Optional[List[Dict[str, Any]]] = None,
        webhooks: Optional[List[Dict[str, Any]]] = None,
        users: Optional[List[Dict[str, Any]]] = None,
        households: Optional[List[Dict[str, Any]]] = None,
        preferences: Optional[Dict[str, Any]] = None,
        **kwargs: Any,  
    ) -> None:
        self.id = id
        self.name = name
        self.slug = slug
        self.categories = categories or []
        self.webhooks = webhooks or []
        self.users = users or []
        self.preferences = preferences or {}
        self.households = households or []
        super().__init__(**kwargs)

    def get_user_count(self) -> int:
        """Get number of users in the group."""
        return len(self.users)

    def get_category_count(self) -> int:
        """Get number of categories in the group."""
        return len(self.categories)

    def get_household_count(self) -> int:
        """Get number of households in the group."""
        return len(self.households)

class GroupSummary(BaseModel):
    """Lightweight group summary for list views."""

    def __init__(
        self,
        id: Optional[str] = None,
        name: str = "",
        slug: Optional[str] = None,
        user_count: Optional[int] = None,
        category_count: Optional[int] = None,
        household_count: Optional[int] = None,
        **kwargs: Any,
    ) -> None:
        self.id = id
        self.name = name
        self.slug = slug
        self.user_count = user_count or 0
        self.category_count = category_count or 0
        self.household_count = household_count or 0
        super().__init__(**kwargs) 

class GroupCreateRequest(BaseModel):
    """Request to create a new group."""

    def __init__(
        self,
        name: str,
        **kwargs: Any,
    ) -> None:
        self.name = name
        super().__init__(**kwargs)

class GroupUpdateRequest(BaseModel):
    """Request to update a group."""

    def __init__(
        self,
        id: str,
        name: Optional[str] = None,
        preferences: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> None:
        self.id = id
        self.name = name
        self.preferences = preferences or {}
        super().__init__(**kwargs)

class GroupFilter(QueryFilter):
    """Filter for group queries."""
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