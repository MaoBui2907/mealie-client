"""
User models for the Mealie SDK.

This module contains data models for users, user profiles, and authentication.
"""

from typing import Any, Dict, List, Optional

from .common import BaseModel, OrderByNullPosition, OrderDirection, QueryFilter


class User(BaseModel):
    """Complete user model with profile and settings."""

    def __init__(
        self,
        username: str = "",
        email: str = "",
        full_name: Optional[str] = None,
        admin: bool = False,
        group: Optional[str] = None,
        household: Optional[str] = None,
        id: Optional[str] = None,
        advanced: bool = False,
        can_invite: bool = False,
        can_manage: bool = False,
        can_organize: bool = False,
        can_manage_household: bool = False,
        auth_method: Optional[str] = None,
        group_id: Optional[str] = None,
        group_slug: Optional[str] = None,
        household_id: Optional[str] = None,
        household_slug: Optional[str] = None,
        tokens: Optional[List[Dict[str, Any]]] = None,
        cache_key: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        self.username = username
        self.email = email
        self.full_name = full_name
        self.admin = admin
        self.group = group
        self.household = household
        self.id = id
        self.advanced = advanced
        self.can_invite = can_invite
        self.can_manage = can_manage
        self.can_organize = can_organize
        self.can_manage_household = can_manage_household
        super().__init__(**kwargs)


class UserCreateRequest(BaseModel):
    """Request model for creating a new user."""

    def __init__(
        self,
        username: str,
        email: str,
        password: str,
        full_name: Optional[str] = None,
        admin: bool = False,
        group: Optional[str] = None,
        household: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        self.username = username
        self.email = email
        self.password = password
        self.full_name = full_name
        self.admin = admin
        self.group = group
        self.household = household
        super().__init__(**kwargs)


class UserUpdateRequest(BaseModel):
    """Request model for updating user information."""

    def __init__(
        self,
        username: Optional[str] = None,
        email: Optional[str] = None,
        full_name: Optional[str] = None,
        admin: Optional[bool] = None,
        group: Optional[str] = None,
        household: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        self.username = username
        self.email = email
        self.full_name = full_name
        self.admin = admin
        self.group = group
        self.household = household
        super().__init__(**kwargs)


class UserSummary(BaseModel):
    """Lightweight user summary for list views."""

    def __init__(
        self,
        id: Optional[str] = None,
        username: str = "",
        email: str = "",
        full_name: Optional[str] = None,
        admin: bool = False,
        group: Optional[str] = None,
        household: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        self.id = id
        self.username = username
        self.email = email
        self.full_name = full_name
        self.admin = admin
        self.group = group
        self.household = household
        super().__init__(**kwargs)


class UserFilter(QueryFilter):
    """Filter options for user queries."""

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
