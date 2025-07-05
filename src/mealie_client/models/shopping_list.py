"""
Shopping list models for the Mealie SDK.

This module contains data models for shopping lists and shopping list items.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from .common import BaseModel, OrderByNullPosition, OrderDirection, QueryFilter, ShoppingListItemStatus, convert_datetime
from .shopping_list_item import ShoppingListItem


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
        
        # Convert items - handle multiple possible field names (API uses 'listItems', test data uses 'list_items')
        items_field = None
        items_data = None
        
        # Check for items in different field names (handle empty arrays)
        if "items" in list_data and list_data["items"] is not None:
            items_field = "items"
            items_data = list_data["items"]
        elif "list_items" in list_data and list_data["list_items"] is not None:
            items_field = "list_items"
            items_data = list_data["list_items"]
        elif "listItems" in list_data and list_data["listItems"] is not None:
            items_field = "listItems"
            items_data = list_data["listItems"]
        
        if items_field and items_data is not None:
            list_data["items"] = [
                ShoppingListItem.from_dict(item) if isinstance(item, dict) else item
                for item in items_data
            ]
            # Remove the original field if it's not "items"
            if items_field != "items":
                del list_data[items_field]
        else:
            list_data["items"] = []
        
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

    @property
    def list_items(self) -> List[ShoppingListItem]:
        """Alias for items to match API response structure."""
        return self.items


class ShoppingListCreateRequest(BaseModel):
    """Request model for creating a new shopping list."""

    def __init__(
        self,
        name: str,
        extras: Optional[Dict[str, Any]] = None,
        created_at: Optional[Union[str, datetime]] = None,
        updated_at: Optional[Union[str, datetime]] = None,
        **kwargs: Any,
    ) -> None:
        self.name = name
        self.extras = extras
        self.created_at = convert_datetime(created_at)
        self.updated_at = convert_datetime(updated_at)
        super().__init__(**kwargs)


class ShoppingListUpdateRequest(BaseModel):
    """Request model for updating shopping list information."""

    def __init__(
        self,
        id: Optional[str] = None,
        group_id: Optional[str] = None,
        user_id: Optional[str] = None,
        name: Optional[str] = None,
        extras: Optional[Dict[str, Any]] = None,
        updated_at: Optional[Union[str, datetime]] = None,
        created_at: Optional[Union[str, datetime]] = None,
        list_items: Optional[List[ShoppingListItem]] = None,
        **kwargs: Any,
    ) -> None:
        self.id = id
        self.group_id = group_id
        self.user_id = user_id
        self.name = name
        self.extras = extras
        self.updated_at = convert_datetime(updated_at)
        self.created_at = convert_datetime(created_at)
        self.list_items = list_items or []
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


class ShoppingListFilter(QueryFilter):
    """Filter options for shopping list queries."""

    def __init__(
        self,
        page: int = 1,
        per_page: int = 50,
        order_by: Optional[str] = None,
        order_direction: OrderDirection = OrderDirection.ASC,
        order_by_null_position: OrderByNullPosition = OrderByNullPosition.LAST,
        search: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            page=page,
            per_page=per_page,
            order_by=order_by,
            order_direction=order_direction,
            order_by_null_position=order_by_null_position,
            search=search,
            **kwargs,
        )