"""
Groups endpoint manager for the Mealie SDK.

Groups in Mealie are read-only via API. Create, update, and delete operations
must be performed through the web interface.
"""

from typing import Any, Dict, List, Optional

from mealie_client.models.user import User

from ..models.group import Group, GroupCreateRequest, GroupFilter, GroupSummary, GroupUpdateRequest
from ..exceptions import NotFoundError
from ..models.common import OrderByNullPosition, OrderDirection


class GroupsManager:
    """Manages group-related API operations.
    
    Note: Groups are read-only via Mealie API. CRUD operations are not supported
    and must be performed through the web interface.
    """

    def __init__(self, client: Any) -> None:
        self.client = client

    async def get_self(self) -> Group:
        """
        Get the current user's group.

        Returns:
            Group object 
            
        Raises:
            MealieAPIError: If the API request fails
        """
        response = await self.client.get("groups/self")
        return Group.from_dict(response)

    async def get_group_preferences(self) -> Dict[str, Any]:
        """
        Get the current user's group preferences.

        Returns:
            Group preferences {
                "id": str,
                "privateGroup": bool,
                "groupId": str,
            }
            
        Raises:
            MealieAPIError: If the API request fails
        """
        response = await self.client.get("groups/preferences")
        return response
    
    async def update_group_preferences(self, preferences: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update the current user's group preferences.
        
        Args:
            preferences: Group preferences to update {
                "privateGroup": bool,
            }
            
        Returns:
            Group preferences {
                "id": str,
                "groupId": str,
                "privateGroup": bool,
            }
        """
        response = await self.client.put("groups/preferences", json_data=preferences)
        return response
    
    async def get_all(self,
        page: int = 1,
        per_page: int = 50,
        order_by: Optional[str] = None,
        order_direction: OrderDirection = OrderDirection.ASC,
        order_by_null_position: OrderByNullPosition = OrderByNullPosition.LAST,
        search: Optional[str] = None,
        accept_language: Optional[str] = None,) -> List[GroupSummary]:
        """
        Get all groups. (Admin only)
        
        Returns:
            List of group summaries
            
        Raises:
            MealieAPIError: If the API request fails
        """
        response = await self.client.get("admin/groups", params=GroupFilter(
            page=page,
            per_page=per_page,
            order_by=order_by,
            order_direction=order_direction,
            order_by_null_position=order_by_null_position,
            search=search,
            accept_language=accept_language,
        ).to_params())
        
        if isinstance(response, list):
            groups_data = response
            metadata = {
                "page": page,
                "per_page": per_page,
                "total": len(response),
                "total_pages": page,
            }
        elif isinstance(response, dict) and "items" in response:
            groups_data = response["items"]
            metadata = {
                "page": response.get("page", page),
                "per_page": response.get("perPage", per_page),
                "total": response.get("total", 0),
                "total_pages": response.get("totalPages", 0),
            }
        else:
            groups_data = []
            metadata = {
                "page": page,
                "per_page": per_page,
                "total": 0,
                "total_pages": 0,
            }

        return [
            GroupSummary.from_dict(group_data) if isinstance(group_data, dict) else group_data
            for group_data in groups_data
        ]

    async def get(self, group_id: str) -> Group:
        """
        Get a specific group by ID. (Admin only)
        
        Args:
            group_id: Group ID identifier
            
        Returns:
            Complete group object
            
        Raises:
            NotFoundError: If group not found
            MealieAPIError: If the API request fails
        """
        try:
            response = await self.client.get(f"admin/groups/{group_id}")
            
            if isinstance(response, bytes):
                response_text = response.decode('utf-8', errors='ignore').lower()
                if '<!doctype html>' in response_text or '<html' in response_text:
                    raise NotFoundError(
                        f"Group '{group_id}' not found",
                        resource_type="group",
                        resource_id=group_id,
                    )
            
            if not isinstance(response, dict):
                raise ValueError("Response must be a dictionary")
            
            return Group.from_dict(response)
        except Exception as e:
            if hasattr(e, 'status_code') and getattr(e, 'status_code') == 404:
                raise NotFoundError(
                    f"Group '{group_id}' not found",
                    resource_type="group",
                    resource_id=group_id,
                )
            raise 
    
    async def create(self, group: GroupCreateRequest) -> Group:
        """
        Create a new group. (Admin only)
        
        Args:
            group: Group object to create
            
        Returns:
            Created group object
            
        Raises:
            MealieAPIError: If the API request fails
        """
        if hasattr(group, 'to_dict'):
            group_data = group.to_dict()
        else:
            group_data = group
        response = await self.client.post("admin/groups", json_data=group_data)
        if isinstance(response, dict):
            return Group.from_dict(response)
        else:
            return response
    
    async def update(self, group_id: str, group: GroupUpdateRequest) -> Group:  
        """
        Update a group. (Admin only)
        
        Args:
            group_id: Group ID identifier
            group: Group object to update
            
        Returns:
            Updated group object
            
        Raises:
            MealieAPIError: If the API request fails
        """
        if hasattr(group, 'to_dict'):
            group_data = group.to_dict()
        else:
            group_data = group
        
        if not isinstance(group_data, dict):
            raise ValueError("Group data must be a dictionary")
        
        response = await self.client.put(f"admin/groups/{group_id}", json_data={
            **group_data,
            "id": group_id,
        })
        if isinstance(response, dict):
            return Group.from_dict(response)
        else:
            return response
    
    async def delete(self, group_id: str) -> bool:
        """
        Delete a group. (Admin only)
        
        Args:
            group_id: Group ID identifier
            
        Returns:
            True if group was deleted, False otherwise
            
        Raises:
            MealieAPIError: If the API request fails
        """
        response = await self.client.delete(f"admin/groups/{group_id}")
        return response