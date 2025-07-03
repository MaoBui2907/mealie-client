"""
Shopping list models for the Mealie SDK.

This module contains data models for shopping lists and shopping list items.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from .common import BaseModel, ShoppingListItemStatus, convert_datetime, safe_get


class ShoppingListItem(BaseModel):
    """Single shopping list item."""

    def __init__(
        self,
        id: Optional[str] = None,
        shopping_list_id: Optional[str] = None,
        checked: bool = False,
        position: int = 0,
        is_food: bool = False,
        note: Optional[str] = None,
        quantity: Optional[float] = None,
        unit: Optional[str] = None,
        food: Optional[str] = None,
        label: Optional[str] = None,
        recipe_references: Optional[List[Dict[str, Any]]] = None,
        created_at: Optional[Union[str, datetime]] = None,
        updated_at: Optional[Union[str, datetime]] = None,
        **kwargs: Any,
    ) -> None:
        self.id = id
        self.shopping_list_id = shopping_list_id
        self.checked = checked
        self.position = position
        self.is_food = is_food
        self.note = note
        self.quantity = quantity
        self.unit = unit
        self.food = food
        self.label = label
        self.recipe_references = recipe_references or []
        self.created_at = convert_datetime(created_at)
        self.updated_at = convert_datetime(updated_at)
        super().__init__(**kwargs)

    @property
    def status(self) -> ShoppingListItemStatus:
        """Get item status based on checked state."""
        return ShoppingListItemStatus.CHECKED if self.checked else ShoppingListItemStatus.UNCHECKED

    def get_display_text(self) -> str:
        """Get display text for the item."""
        parts = []
        
        if self.quantity:
            parts.append(str(self.quantity))
        if self.unit:
            parts.append(self.unit)
        if self.food:
            parts.append(self.food)
        elif self.label:
            parts.append(self.label)
            
        display = " ".join(parts)
        
        if self.note:
            display += f" ({self.note})"
            
        return display

    def has_recipe_references(self) -> bool:
        """Check if item has recipe references."""
        return len(self.recipe_references) > 0


class ShoppingList(BaseModel):
    """Complete shopping list with items."""

    def __init__(
        self,
        id: Optional[str] = None,
        group_id: Optional[str] = None,
        user_id: Optional[str] = None,
        name: str = "",
        items: Optional[List[ShoppingListItem]] = None,
        recipe_references: Optional[List[Dict[str, Any]]] = None,
        created_at: Optional[Union[str, datetime]] = None,
        updated_at: Optional[Union[str, datetime]] = None,
        **kwargs: Any,
    ) -> None:
        self.id = id
        self.group_id = group_id
        self.user_id = user_id
        self.name = name
        self.items = items or []
        self.recipe_references = recipe_references or []
        self.created_at = convert_datetime(created_at)
        self.updated_at = convert_datetime(updated_at)
        super().__init__(**kwargs)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ShoppingList":
        """Create a ShoppingList instance from a dictionary."""
        list_data = data.copy()
        
        # Convert items
        if "items" in list_data and list_data["items"]:
            list_data["items"] = [
                ShoppingListItem.from_dict(item) if isinstance(item, dict) else item
                for item in list_data["items"]
            ]
        
        return cls(**list_data)

    def get_item_count(self) -> int:
        """Get total number of items."""
        return len(self.items)

    def get_checked_count(self) -> int:
        """Get number of checked items."""
        return sum(1 for item in self.items if item.checked)

    def get_unchecked_count(self) -> int:
        """Get number of unchecked items."""
        return sum(1 for item in self.items if not item.checked)

    def get_completion_percentage(self) -> float:
        """Get completion percentage (0-100)."""
        total = self.get_item_count()
        if total == 0:
            return 0.0
        return (self.get_checked_count() / total) * 100

    def get_items_by_status(self, status: ShoppingListItemStatus) -> List[ShoppingListItem]:
        """Get items filtered by status."""
        checked = status == ShoppingListItemStatus.CHECKED
        return [item for item in self.items if item.checked == checked]

    def is_complete(self) -> bool:
        """Check if all items are checked."""
        return self.get_item_count() > 0 and self.get_unchecked_count() == 0


class ShoppingListCreateRequest(BaseModel):
    """Request model for creating a new shopping list."""

    def __init__(
        self,
        name: str,
        items: Optional[List[Dict[str, Any]]] = None,
        **kwargs: Any,
    ) -> None:
        self.name = name
        self.items = items or []
        super().__init__(**kwargs)


class ShoppingListUpdateRequest(BaseModel):
    """Request model for updating shopping list information."""

    def __init__(
        self,
        name: Optional[str] = None,
        items: Optional[List[Dict[str, Any]]] = None,
        **kwargs: Any,
    ) -> None:
        self.name = name
        self.items = items
        super().__init__(**kwargs)


class ShoppingListItemCreateRequest(BaseModel):
    """Request model for creating a shopping list item."""

    def __init__(
        self,
        checked: bool = False,
        position: int = 0,
        is_food: bool = False,
        note: Optional[str] = None,
        quantity: Optional[float] = None,
        unit: Optional[str] = None,
        food: Optional[str] = None,
        label: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        self.checked = checked
        self.position = position
        self.is_food = is_food
        self.note = note
        self.quantity = quantity
        self.unit = unit
        self.food = food
        self.label = label
        super().__init__(**kwargs)


class ShoppingListItemUpdateRequest(BaseModel):
    """Request model for updating a shopping list item."""

    def __init__(
        self,
        checked: Optional[bool] = None,
        position: Optional[int] = None,
        is_food: Optional[bool] = None,
        note: Optional[str] = None,
        quantity: Optional[float] = None,
        unit: Optional[str] = None,
        food: Optional[str] = None,
        label: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        self.checked = checked
        self.position = position
        self.is_food = is_food
        self.note = note
        self.quantity = quantity
        self.unit = unit
        self.food = food
        self.label = label
        super().__init__(**kwargs)


class ShoppingListSummary(BaseModel):
    """Lightweight shopping list summary for list views."""

    def __init__(
        self,
        id: Optional[str] = None,
        name: str = "",
        item_count: int = 0,
        checked_count: int = 0,
        created_at: Optional[Union[str, datetime]] = None,
        updated_at: Optional[Union[str, datetime]] = None,
        **kwargs: Any,
    ) -> None:
        self.id = id
        self.name = name
        self.item_count = item_count
        self.checked_count = checked_count
        self.created_at = convert_datetime(created_at)
        self.updated_at = convert_datetime(updated_at)
        super().__init__(**kwargs)

    def get_completion_percentage(self) -> float:
        """Get completion percentage (0-100)."""
        if self.item_count == 0:
            return 0.0
        return (self.checked_count / self.item_count) * 100

    def is_complete(self) -> bool:
        """Check if all items are checked."""
        return self.item_count > 0 and self.checked_count == self.item_count


class ShoppingListFilter(BaseModel):
    """Filter options for shopping list queries."""

    def __init__(
        self,
        page: int = 1,
        per_page: int = 50,
        order_by: Optional[str] = None,
        order_direction: str = "asc",
        search: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        self.page = page
        self.per_page = per_page
        self.order_by = order_by
        self.order_direction = order_direction
        self.search = search
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
            
        return params 