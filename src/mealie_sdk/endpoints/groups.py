"""
Groups endpoint manager for the Mealie SDK.
"""

from typing import Any, Dict, List, Union

from ..models.group import Group, GroupCreateRequest, GroupUpdateRequest, GroupSummary
from ..exceptions import NotFoundError


class GroupsManager:
    """Manages group-related API operations."""

    def __init__(self, client: Any) -> None:
        self.client = client

    async def get_all(self) -> List[GroupSummary]:
        """Get all groups."""
        response = await self.client.get("groups")
        
        if isinstance(response, list):
            groups_data = response
        elif isinstance(response, dict) and "items" in response:
            groups_data = response["items"]
        else:
            groups_data = []

        return [
            GroupSummary.from_dict(group_data) if isinstance(group_data, dict) else group_data
            for group_data in groups_data
        ]

    async def get(self, group_id: str) -> Group:
        """Get a specific group by ID."""
        try:
            response = await self.client.get(f"groups/{group_id}")
            return Group.from_dict(response) if isinstance(response, dict) else response
        except Exception as e:
            if hasattr(e, 'status_code') and e.status_code == 404:
                raise NotFoundError(
                    f"Group '{group_id}' not found",
                    resource_type="group",
                    resource_id=group_id,
                )
            raise

    async def create(self, group_data: Union[GroupCreateRequest, Dict[str, Any]]) -> Group:
        """Create a new group."""
        if isinstance(group_data, GroupCreateRequest):
            data = group_data.to_dict()
        else:
            data = group_data

        response = await self.client.post("groups", json_data=data)
        return Group.from_dict(response) if isinstance(response, dict) else response

    async def update(
        self,
        group_id: str,
        group_data: Union[GroupUpdateRequest, Dict[str, Any]],
    ) -> Group:
        """Update an existing group."""
        if isinstance(group_data, GroupUpdateRequest):
            data = group_data.to_dict()
        else:
            data = group_data

        try:
            response = await self.client.put(f"groups/{group_id}", json_data=data)
            return Group.from_dict(response) if isinstance(response, dict) else response
        except Exception as e:
            if hasattr(e, 'status_code') and e.status_code == 404:
                raise NotFoundError(
                    f"Group '{group_id}' not found",
                    resource_type="group",
                    resource_id=group_id,
                )
            raise

    async def delete(self, group_id: str) -> bool:
        """Delete a group."""
        try:
            await self.client.delete(f"groups/{group_id}")
            return True
        except Exception as e:
            if hasattr(e, 'status_code') and e.status_code == 404:
                raise NotFoundError(
                    f"Group '{group_id}' not found",
                    resource_type="group",
                    resource_id=group_id,
                )
            raise 