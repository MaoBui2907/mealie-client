"""
Shopping lists endpoint manager for the Mealie SDK.
"""

from typing import Any, Dict, List, Union

from ..models.shopping_list import (
    ShoppingList,
    ShoppingListCreateRequest,
    ShoppingListUpdateRequest,
    ShoppingListSummary,
    ShoppingListItem,
    ShoppingListItemCreateRequest,
    ShoppingListItemUpdateRequest,
)
from ..exceptions import NotFoundError


class ShoppingListsManager:
    """Manages shopping list-related API operations."""

    def __init__(self, client: Any) -> None:
        self.client = client

    async def get_all(self) -> List[ShoppingListSummary]:
        """Get all shopping lists."""
        response = await self.client.get("groups/shopping/lists")
        
        if isinstance(response, list):
            lists_data = response
        elif isinstance(response, dict) and "items" in response:
            lists_data = response["items"]
        else:
            lists_data = []

        return [
            ShoppingListSummary.from_dict(list_data) if isinstance(list_data, dict) else list_data
            for list_data in lists_data
        ]

    async def get(self, list_id: str) -> ShoppingList:
        """Get a specific shopping list by ID."""
        try:
            response = await self.client.get(f"groups/shopping/lists/{list_id}")
            return ShoppingList.from_dict(response) if isinstance(response, dict) else response
        except Exception as e:
            if hasattr(e, 'status_code') and e.status_code == 404:
                raise NotFoundError(
                    f"Shopping list '{list_id}' not found",
                    resource_type="shopping_list",
                    resource_id=list_id,
                )
            raise

    async def create(self, list_data: Union[ShoppingListCreateRequest, Dict[str, Any]]) -> ShoppingList:
        """Create a new shopping list."""
        if isinstance(list_data, ShoppingListCreateRequest):
            data = list_data.to_dict()
        else:
            data = list_data

        response = await self.client.post("groups/shopping/lists", json_data=data)
        return ShoppingList.from_dict(response) if isinstance(response, dict) else response

    async def update(
        self,
        list_id: str,
        list_data: Union[ShoppingListUpdateRequest, Dict[str, Any]],
    ) -> ShoppingList:
        """Update an existing shopping list."""
        if isinstance(list_data, ShoppingListUpdateRequest):
            data = list_data.to_dict()
        else:
            data = list_data

        try:
            response = await self.client.put(f"groups/shopping/lists/{list_id}", json_data=data)
            return ShoppingList.from_dict(response) if isinstance(response, dict) else response
        except Exception as e:
            if hasattr(e, 'status_code') and e.status_code == 404:
                raise NotFoundError(
                    f"Shopping list '{list_id}' not found",
                    resource_type="shopping_list",
                    resource_id=list_id,
                )
            raise

    async def delete(self, list_id: str) -> bool:
        """Delete a shopping list."""
        try:
            await self.client.delete(f"groups/shopping/lists/{list_id}")
            return True
        except Exception as e:
            if hasattr(e, 'status_code') and e.status_code == 404:
                raise NotFoundError(
                    f"Shopping list '{list_id}' not found",
                    resource_type="shopping_list",
                    resource_id=list_id,
                )
            raise

    async def add_item(
        self,
        list_id: str,
        item_data: Union[ShoppingListItemCreateRequest, Dict[str, Any]],
    ) -> ShoppingListItem:
        """Add an item to a shopping list."""
        if isinstance(item_data, ShoppingListItemCreateRequest):
            data = item_data.to_dict()
        else:
            data = item_data

        response = await self.client.post(f"groups/shopping/lists/{list_id}/items", json_data=data)
        return ShoppingListItem.from_dict(response) if isinstance(response, dict) else response

    async def update_item(
        self,
        list_id: str,
        item_id: str,
        item_data: Union[ShoppingListItemUpdateRequest, Dict[str, Any]],
    ) -> ShoppingListItem:
        """Update a shopping list item."""
        if isinstance(item_data, ShoppingListItemUpdateRequest):
            data = item_data.to_dict()
        else:
            data = item_data

        response = await self.client.put(
            f"groups/shopping/lists/{list_id}/items/{item_id}",
            json_data=data
        )
        return ShoppingListItem.from_dict(response) if isinstance(response, dict) else response

    async def delete_item(self, list_id: str, item_id: str) -> bool:
        """Delete an item from a shopping list."""
        await self.client.delete(f"groups/shopping/lists/{list_id}/items/{item_id}")
        return True 