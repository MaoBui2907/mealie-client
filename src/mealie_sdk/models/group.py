"""
Group models for the Mealie SDK.

This module contains data models for groups and group management.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from .common import BaseModel, convert_datetime, safe_get


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
        preferences: Optional[Dict[str, Any]] = None,
        created_at: Optional[Union[str, datetime]] = None,
        updated_at: Optional[Union[str, datetime]] = None,
        **kwargs: Any,
    ) -> None:
        self.id = id
        self.name = name
        self.slug = slug
        self.categories = categories or []
        self.webhooks = webhooks or []
        self.users = users or []
        self.preferences = preferences or {}
        self.created_at = convert_datetime(created_at)
        self.updated_at = convert_datetime(updated_at)
        super().__init__(**kwargs)

    def get_user_count(self) -> int:
        """Get number of users in the group."""
        return len(self.users)

    def get_category_count(self) -> int:
        """Get number of categories in the group."""
        return len(self.categories)


class GroupCreateRequest(BaseModel):
    """Request model for creating a new group."""

    def __init__(
        self,
        name: str,
        **kwargs: Any,
    ) -> None:
        self.name = name
        super().__init__(**kwargs)


class GroupUpdateRequest(BaseModel):
    """Request model for updating group information."""

    def __init__(
        self,
        name: Optional[str] = None,
        preferences: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> None:
        self.name = name
        self.preferences = preferences
        super().__init__(**kwargs)


class GroupSummary(BaseModel):
    """Lightweight group summary for list views."""

    def __init__(
        self,
        id: Optional[str] = None,
        name: str = "",
        slug: Optional[str] = None,
        user_count: int = 0,
        category_count: int = 0,
        created_at: Optional[Union[str, datetime]] = None,
        **kwargs: Any,
    ) -> None:
        self.id = id
        self.name = name
        self.slug = slug
        self.user_count = user_count
        self.category_count = category_count
        self.created_at = convert_datetime(created_at)
        super().__init__(**kwargs) 