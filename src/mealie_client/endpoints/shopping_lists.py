"""
Shopping lists endpoint manager for the Mealie SDK.
"""

from typing import Any, Dict, List, Union
import warnings

from ..models.shopping_list import (
    ShoppingList,
    ShoppingListCreateRequest,
    ShoppingListUpdateRequest,
    ShoppingListSummary,
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
        response = await self.client.get("households/shopping/lists")
        
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
            response = await self.client.get(f"households/shopping/lists/{list_id}")
            return ShoppingList.from_dict(response) if isinstance(response, dict) else response
        except Exception as e:
            if hasattr(e, 'status_code') and getattr(e, 'status_code') == 404:
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

        response = await self.client.post("households/shopping/lists", json_data=data)
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
            response = await self.client.put(f"households/shopping/lists/{list_id}", json_data=data)
            return ShoppingList.from_dict(response) if isinstance(response, dict) else response
        except Exception as e:
            if hasattr(e, 'status_code') and getattr(e, 'status_code') == 404:
                raise NotFoundError(
                    f"Shopping list '{list_id}' not found",
                    resource_type="shopping_list",
                    resource_id=list_id,
                )
            raise

    async def delete(self, list_id: str) -> bool:
        """Delete a shopping list."""
        try:
            await self.client.delete(f"households/shopping/lists/{list_id}")
            return True
        except Exception as e:
            if hasattr(e, 'status_code') and getattr(e, 'status_code') == 404:
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
    ) -> ShoppingList:
        """
        DEPRECATED: Add an item to a shopping list.
        
        This method is deprecated as the Mealie API doesn't support direct item operations.
        Use add_recipe_ingredients() instead.
        """
        warnings.warn(
            "add_item() is deprecated. The Mealie API doesn't support direct item operations. "
            "Use add_recipe_ingredients() instead.",
            DeprecationWarning,
            stacklevel=2
        )
        
        if isinstance(item_data, ShoppingListItemCreateRequest):
            data = item_data.to_dict()
        else:
            data = item_data

        response = await self.client.post(f"households/shopping/lists/{list_id}/items", json_data=data)
        return ShoppingList.from_dict(response) if isinstance(response, dict) else response

    async def update_item(
        self,
        list_id: str,
        item_id: str,
        item_data: Union[ShoppingListItemUpdateRequest, Dict[str, Any]],
    ) -> ShoppingList:
        """
        DEPRECATED: Update a shopping list item.
        
        This method is deprecated as the Mealie API doesn't support direct item operations.
        """
        warnings.warn(
            "update_item() is deprecated. The Mealie API doesn't support direct item operations.",
            DeprecationWarning,
            stacklevel=2
        )
        
        if isinstance(item_data, ShoppingListItemUpdateRequest):
            data = item_data.to_dict()
        else:
            data = item_data

        response = await self.client.put(
            f"households/shopping/lists/{list_id}/items/{item_id}",
            json_data=data
        )
        return ShoppingList.from_dict(response) if isinstance(response, dict) else response

    async def delete_item(self, list_id: str, item_id: str) -> bool:
        """
        DEPRECATED: Delete an item from a shopping list.
        
        This method is deprecated as the Mealie API doesn't support direct item operations.
        """
        warnings.warn(
            "delete_item() is deprecated. The Mealie API doesn't support direct item operations.",
            DeprecationWarning,
            stacklevel=2
        )
        
        await self.client.delete(f"households/shopping/lists/{list_id}/items/{item_id}")
        return True

    async def add_recipe_ingredients(
        self,
        list_id: str,
        recipe_data: List[Dict[str, Any]],
    ) -> ShoppingList:
        """
        Add recipe ingredients to a shopping list.
        
        Args:
            list_id: Shopping list ID
            recipe_data: List of recipe ingredient data following API schema
            
        Returns:
            Updated shopping list
        """
        response = await self.client.post(f"households/shopping/lists/{list_id}/recipe", json_data=recipe_data)
        return ShoppingList.from_dict(response) if isinstance(response, dict) else response

    async def add_single_recipe_ingredients(
        self,
        list_id: str,
        recipe_id: str,
    ) -> ShoppingList:
        """
        Add single recipe ingredients to a shopping list.
        
        Args:
            list_id: Shopping list ID
            recipe_id: Recipe ID to add ingredients from
            
        Returns:
            Updated shopping list
        """
        response = await self.client.post(f"households/shopping/lists/{list_id}/recipe/{recipe_id}")
        return ShoppingList.from_dict(response) if isinstance(response, dict) else response

    async def remove_recipe_ingredients(
        self,
        list_id: str,
        recipe_id: str,
        decrement_data: Dict[str, Any],
    ) -> ShoppingList:
        """
        Remove recipe ingredients from a shopping list.
        
        Args:
            list_id: Shopping list ID
            recipe_id: Recipe ID to remove ingredients from
            decrement_data: Data with recipeDecrementQuantity
            
        Returns:
            Updated shopping list
        """
        response = await self.client.post(
            f"households/shopping/lists/{list_id}/recipe/{recipe_id}/delete",
            json_data=decrement_data
        )
        return ShoppingList.from_dict(response) if isinstance(response, dict) else response

    async def update_label_settings(
        self,
        list_id: str,
        label_settings: List[Dict[str, Any]],
    ) -> ShoppingList:
        """
        Update label settings for a shopping list.
        
        Args:
            list_id: Shopping list ID
            label_settings: List of label setting objects
            
        Returns:
            Updated shopping list
        """
        response = await self.client.put(
            f"households/shopping/lists/{list_id}/label-settings",
            json_data=label_settings
        )
        return ShoppingList.from_dict(response) if isinstance(response, dict) else response

    async def clear_checked_items(self, list_id: str) -> ShoppingList:
        """
        DEPRECATED: Clear all checked items from a shopping list.
        
        This method is deprecated as the Mealie API doesn't support direct item operations.
        """
        warnings.warn(
            "clear_checked_items() is deprecated. The Mealie API doesn't support direct item operations.",
            DeprecationWarning,
            stacklevel=2
        )
        
        response = await self.client.delete(f"households/shopping/lists/{list_id}/items/checked")
        return ShoppingList.from_dict(response) if isinstance(response, dict) else response 