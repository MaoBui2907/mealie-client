"""
Mealie SDK API endpoint managers.

This package contains endpoint managers that handle specific API functionality
for different Mealie resources like recipes, users, groups, meal plans, and shopping lists.
"""

from .recipes import RecipesManager
from .users import UsersManager
from .groups import GroupsManager
from .meal_plans import MealPlansManager
from .shopping_lists import ShoppingListsManager

__all__ = [
    "RecipesManager",
    "UsersManager",
    "GroupsManager", 
    "MealPlansManager",
    "ShoppingListsManager",
] 