"""
User models for the Mealie SDK.

This module contains data models for users, user profiles, and authentication.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from .common import BaseModel, UserRole, convert_datetime, safe_get


class User(BaseModel):
    """Complete user model with profile and settings."""

    def __init__(
        self,
        id: Optional[str] = None,
        username: str = "",
        email: str = "",
        full_name: Optional[str] = None,
        admin: bool = False,
        group: Optional[str] = None,
        group_id: Optional[str] = None,
        favorite_recipes: Optional[List[str]] = None,
        can_invite: bool = False,
        can_manage: bool = False,
        can_organize: bool = False,
        advanced: bool = False,
        auth_method: str = "Mealie",
        password_reset_time: Optional[Union[str, datetime]] = None,
        login_attemps: int = 0,
        locked_at: Optional[Union[str, datetime]] = None,
        created_at: Optional[Union[str, datetime]] = None,
        updated_at: Optional[Union[str, datetime]] = None,
        **kwargs: Any,
    ) -> None:
        self.id = id
        self.username = username
        self.email = email
        self.full_name = full_name
        self.admin = admin
        self.group = group
        self.group_id = group_id
        self.favorite_recipes = favorite_recipes or []
        self.can_invite = can_invite
        self.can_manage = can_manage
        self.can_organize = can_organize
        self.advanced = advanced
        self.auth_method = auth_method
        self.password_reset_time = convert_datetime(password_reset_time)
        self.login_attemps = login_attemps
        self.locked_at = convert_datetime(locked_at)
        self.created_at = convert_datetime(created_at)
        self.updated_at = convert_datetime(updated_at)
        super().__init__(**kwargs)

    @property
    def role(self) -> UserRole:
        """Get user role based on admin status."""
        return UserRole.ADMIN if self.admin else UserRole.USER

    def is_admin(self) -> bool:
        """Check if user is an admin."""
        return self.admin

    def is_locked(self) -> bool:
        """Check if user account is locked."""
        return self.locked_at is not None

    def get_display_name(self) -> str:
        """Get display name (full name if available, otherwise username)."""
        return self.full_name or self.username


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
        **kwargs: Any,
    ) -> None:
        self.username = username
        self.email = email
        self.password = password
        self.full_name = full_name
        self.admin = admin
        self.group = group
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
        can_invite: Optional[bool] = None,
        can_manage: Optional[bool] = None,
        can_organize: Optional[bool] = None,
        advanced: Optional[bool] = None,
        **kwargs: Any,
    ) -> None:
        self.username = username
        self.email = email
        self.full_name = full_name
        self.admin = admin
        self.group = group
        self.can_invite = can_invite
        self.can_manage = can_manage
        self.can_organize = can_organize
        self.advanced = advanced
        super().__init__(**kwargs)


class UserPasswordChangeRequest(BaseModel):
    """Request model for changing user password."""

    def __init__(
        self,
        current_password: str,
        new_password: str,
        **kwargs: Any,
    ) -> None:
        self.current_password = current_password
        self.new_password = new_password
        super().__init__(**kwargs)


class UserPasswordResetRequest(BaseModel):
    """Request model for password reset."""

    def __init__(
        self,
        email: str,
        **kwargs: Any,
    ) -> None:
        self.email = email
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
        created_at: Optional[Union[str, datetime]] = None,
        **kwargs: Any,
    ) -> None:
        self.id = id
        self.username = username
        self.email = email
        self.full_name = full_name
        self.admin = admin
        self.group = group
        self.created_at = convert_datetime(created_at)
        super().__init__(**kwargs)

    def get_display_name(self) -> str:
        """Get display name (full name if available, otherwise username)."""
        return self.full_name or self.username


class UserFilter(BaseModel):
    """Filter options for user queries."""

    def __init__(
        self,
        page: int = 1,
        per_page: int = 50,
        order_by: Optional[str] = None,
        order_direction: str = "asc",
        search: Optional[str] = None,
        admin_only: Optional[bool] = None,
        group: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        self.page = page
        self.per_page = per_page
        self.order_by = order_by
        self.order_direction = order_direction
        self.search = search
        self.admin_only = admin_only
        self.group = group
        super().__init__(**kwargs)

    def to_params(self) -> Dict[str, Any]:
        """Convert filter to query parameters."""
        params = {
            "page": self.page,
            "perPage": self.per_page,
        }
        
        if self.order_by:
            params["orderBy"] = self.order_by
            params["orderDirection"] = self.order_direction
            
        if self.search:
            params["search"] = self.search
            
        if self.admin_only is not None:
            params["adminOnly"] = str(self.admin_only).lower()
            
        if self.group:
            params["group"] = self.group
            
        return params 