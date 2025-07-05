"""
Shopping list item models for the Mealie SDK.

This module contains data models for shopping list items.
"""

from typing import Any, Dict, List, Optional

from .common import BaseModel
from .unit import Unit
from .food import Food
from .label import Label


class ShoppingListItem(BaseModel):
    """Shopping list item."""
    
    def __init__(
        self,
        id: Optional[str] = None,
        group_id: Optional[str] = None,
        household_id: Optional[str] = None,
        quantity: Optional[float] = None,
        recipe_references: Optional[List[str]] = None,
        unit: Optional[Unit] = None,
        food: Optional[Food] = None,
        note: Optional[str] = None,
        is_food: bool = False,
        disable_amount: bool = False,
        display: Optional[str] = None,
        shopping_list_id: Optional[str] = None,
        checked: bool = False,
        position: int = 0,
        food_id: Optional[str] = None,
        label_id: Optional[str] = None,
        unit_id: Optional[str] = None,
        extras: Optional[Dict[str, Any]] = None,
        label: Optional[Label] = None,
        **kwargs: Any,
    ) -> None:
        self.id = id
        self.group_id = group_id
        self.household_id = household_id
        self.quantity = quantity
        self.recipe_references = recipe_references
        self.unit = unit
        self.food = food
        self.note = note
        self.checked = checked
        self.position = position
        self.is_food = is_food
        self.note = note
        self.quantity = quantity
        self.unit = unit
        self.food = food
        self.label = label
        super().__init__(**kwargs)

class ShoppingListItemCreateRequest(BaseModel):
    """Request model for creating a shopping list item."""
    
    def __init__(
        self,
        quantity: Optional[float] = None,
        unit: Optional[Unit] = None,
        food: Optional[Food] = None,
        note: Optional[str] = None,
        is_food: bool = False,
        disable_amount: bool = False,
        display: Optional[str] = None,
        shopping_list_id: Optional[str] = None,
        checked: bool = False,
        position: int = 0,
        food_id: Optional[str] = None,
        label_id: Optional[str] = None,
        unit_id: Optional[str] = None,
        extras: Optional[Dict[str, Any]] = None,
        recipe_references: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> None:
        self.quantity = quantity
        self.unit = unit
        self.food = food
        self.note = note
        self.is_food = is_food
        self.disable_amount = disable_amount
        self.display = display
        self.shopping_list_id = shopping_list_id
        self.checked = checked
        self.position = position
        self.food_id = food_id
        self.label_id = label_id
        self.unit_id = unit_id
        self.extras = extras
        self.recipe_references = recipe_references
        super().__init__(**kwargs)

class ShoppingListItemUpdateRequest(BaseModel):
    """Request model for updating a shopping list item."""
    
    def __init__(
        self,
        quantity: Optional[float] = None,
        unit: Optional[Unit] = None,
        food: Optional[Food] = None,
        note: Optional[str] = None,
        is_food: bool = False,
        disable_amount: bool = False,
        display: Optional[str] = None,
        shopping_list_id: Optional[str] = None,
        checked: bool = False,
        position: int = 0,
        food_id: Optional[str] = None,
        label_id: Optional[str] = None,
        unit_id: Optional[str] = None,
        extras: Optional[Dict[str, Any]] = None,
        recipe_references: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> None:
        self.quantity = quantity
        self.unit = unit
        self.food = food
        self.note = note
        self.is_food = is_food
        self.disable_amount = disable_amount
        self.display = display
        self.shopping_list_id = shopping_list_id
        self.checked = checked
        self.position = position
        self.food_id = food_id
        self.label_id = label_id
        self.unit_id = unit_id
        self.extras = extras
        self.recipe_references = recipe_references
        super().__init__(**kwargs)
