"""
Users endpoint manager for the Mealie SDK.
"""

from typing import Any, Dict, List, Optional, Union

from ..models.user import User, UserCreateRequest, UserUpdateRequest, UserSummary, UserFilter
from ..exceptions import NotFoundError


class UsersManager:
    """Manages user-related API operations."""

    def __init__(self, client: Any) -> None:
        self.client = client

    async def get_all(self, page: int = 1, per_page: int = 50) -> List[UserSummary]:
        """Get all users with pagination."""
        params = {"page": page, "perPage": per_page}
        response = await self.client.get("users", params=params)
        
        if isinstance(response, dict) and "items" in response:
            users_data = response["items"]
        elif isinstance(response, list):
            users_data = response
        else:
            users_data = []

        return [
            UserSummary.from_dict(user_data) if isinstance(user_data, dict) else user_data
            for user_data in users_data
        ]

    async def get(self, user_id: str) -> User:
        """Get a specific user by ID."""
        try:
            response = await self.client.get(f"users/{user_id}")
            return User.from_dict(response) if isinstance(response, dict) else response
        except Exception as e:
            if hasattr(e, 'status_code') and e.status_code == 404:
                raise NotFoundError(
                    f"User '{user_id}' not found",
                    resource_type="user",
                    resource_id=user_id,
                )
            raise

    async def create(self, user_data: Union[UserCreateRequest, Dict[str, Any]]) -> User:
        """Create a new user."""
        if isinstance(user_data, UserCreateRequest):
            data = user_data.to_dict()
        else:
            data = user_data

        response = await self.client.post("users", json_data=data)
        return User.from_dict(response) if isinstance(response, dict) else response

    async def update(
        self,
        user_id: str,
        user_data: Union[UserUpdateRequest, Dict[str, Any]],
    ) -> User:
        """Update an existing user."""
        if isinstance(user_data, UserUpdateRequest):
            data = user_data.to_dict()
        else:
            data = user_data

        try:
            response = await self.client.put(f"users/{user_id}", json_data=data)
            return User.from_dict(response) if isinstance(response, dict) else response
        except Exception as e:
            if hasattr(e, 'status_code') and e.status_code == 404:
                raise NotFoundError(
                    f"User '{user_id}' not found",
                    resource_type="user",
                    resource_id=user_id,
                )
            raise

    async def delete(self, user_id: str) -> bool:
        """Delete a user."""
        try:
            await self.client.delete(f"users/{user_id}")
            return True
        except Exception as e:
            if hasattr(e, 'status_code') and e.status_code == 404:
                raise NotFoundError(
                    f"User '{user_id}' not found",
                    resource_type="user",
                    resource_id=user_id,
                )
            raise

    async def get_current(self) -> User:
        """Get current authenticated user."""
        response = await self.client.get("users/self")
        return User.from_dict(response) if isinstance(response, dict) else response 