"""
Users endpoint manager for the Mealie SDK.
"""

from typing import Any, Dict, List, Optional, Union

from mealie_client.models.common import OrderByNullPosition, OrderDirection

from ..models.user import (
    User,
    UserCreateRequest,
    UserFilter,
    UserUpdateRequest,
    UserSummary,
)
from ..exceptions import NotFoundError


class UsersManager:
    """Manages user-related API operations."""

    def __init__(self, client: Any) -> None:
        self.client = client

    async def get_all(
        self,
        page: int = 1,
        per_page: int = 50,
        order_by: Optional[str] = None,
        order_direction: OrderDirection = OrderDirection.ASC,
        order_by_null_position: OrderByNullPosition = OrderByNullPosition.LAST,
        accept_language: Optional[str] = None,
    ) -> List[UserSummary]:
        """Get all users with pagination. Only admin can get all users."""

        response = await self.client.get(
            "admin/users",
            params=UserFilter(
                page=page,
                per_page=per_page,
                order_by=order_by,
                order_direction=order_direction,
                order_by_null_position=order_by_null_position,
                accept_language=accept_language,
            ).to_params(),
        )

        if isinstance(response, dict) and "items" in response:
            users_data = response["items"]
        elif isinstance(response, list):
            users_data = response
        else:
            users_data = []

        return [
            UserSummary.from_dict(user_data)
            if isinstance(user_data, dict)
            else user_data
            for user_data in users_data
        ]

    async def get(self, user_id: str) -> User:
        """Get a specific user by ID. Only admin can get a user."""
        try:
            response = await self.client.get(f"admin/users/{user_id}")
            return User.from_dict(response) if isinstance(response, dict) else response
        except Exception as e:
            if hasattr(e, "status_code") and getattr(e, "status_code") == 404:
                raise NotFoundError(
                    f"User '{user_id}' not found",
                    resource_type="user",
                    resource_id=user_id,
                )
            raise

    async def create(self, user_data: Union[UserCreateRequest, Dict[str, Any]]) -> User:
        """Create a new user. Only admin can create a user."""
        if isinstance(user_data, UserCreateRequest):
            data = user_data.to_dict()
        else:
            data = user_data

        response = await self.client.post("admin/users", json_data=data)
        return User.from_dict(response) if isinstance(response, dict) else response

    async def update(
        self,
        user_id: str,
        user_data: Union[UserUpdateRequest, Dict[str, Any]],
    ) -> User:
        """Update an existing user. Only admin can update a user."""
        if isinstance(user_data, UserUpdateRequest):
            data = user_data.to_dict()
        else:
            data = user_data

        try:
            response = await self.client.put(f"admin/users/{user_id}", json_data=data)
            return User.from_dict(response) if isinstance(response, dict) else response
        except Exception as e:
            if hasattr(e, "status_code") and getattr(e, "status_code") == 404:
                raise NotFoundError(
                    f"User '{user_id}' not found",
                    resource_type="user",
                    resource_id=user_id,
                )
            raise

    async def delete(self, user_id: str) -> bool:
        """Delete a user."""
        try:
            await self.client.delete(f"admin/users/{user_id}")
            return True
        except Exception as e:
            if hasattr(e, "status_code") and getattr(e, "status_code") == 404:
                raise NotFoundError(
                    f"User '{user_id}' not found",
                    resource_type="user",
                    resource_id=user_id,
                )
            raise

    async def get_self(self, accept_language: Optional[str] = None) -> User:
        """Get current authenticated user."""
        response = await self.client.get(
            "users/self",
            params=UserFilter(accept_language=accept_language).to_params(),
        )
        return User.from_dict(response) if isinstance(response, dict) else response