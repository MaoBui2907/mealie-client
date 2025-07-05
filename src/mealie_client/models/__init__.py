"""
Mealie SDK data models.

This package contains all data models used by the Mealie SDK for representing
recipes, users, groups, meal plans, shopping lists, and other entities.
"""

# Common models and utilities
from .common import (
    BaseModel,
    # Enums
    RecipeVisibility,
    UserRole,
    MealPlanType,
    ShoppingListItemStatus,
    RecipeScale,
    TimeUnit,
    OrderDirection,
    # Common data structures
    Nutrition,
    RecipeIngredient,
    RecipeInstruction,
    RecipeAsset,
    RecipeSettings,
    RecipeCategory,
    RecipeTag,
    RecipeTool,
    PaginationInfo,
    QueryFilter,
    DateRange,
    APIResponse,
    ErrorDetail,
    # Utility functions
    convert_datetime,
    convert_date,
    safe_get,
    filter_none_values,
)

# Recipe models
from .recipe import (
    Recipe,
    RecipeCreateRequest,
    RecipeUpdateRequest,
    RecipeSummary,
    RecipeFilter,
    RecipeSuggestionsFilter,
)

# User models
from .user import (
    User,
    UserCreateRequest,
    UserUpdateRequest,
    UserSummary,
    UserFilter,
)

# Group models
from .group import (
    Group,
    GroupSummary,
)

# Meal plan models
from .meal_plan import (
    MealPlan,
    MealPlanCreateRequest,
    MealPlanUpdateRequest,
    MealPlanFilter,
)

# Shopping list models
from .shopping_list import (
    ShoppingList,
    ShoppingListCreateRequest,
    ShoppingListUpdateRequest,
    ShoppingListSummary,
    ShoppingListFilter,
)

# Shopping list item models
from .shopping_list_item import (
    ShoppingListItem,
    ShoppingListItemCreateRequest,
    ShoppingListItemUpdateRequest,
)

# Unit models
from .unit import (
    Unit,
    UnitCreateRequest,
    UnitUpdateRequest,
    UnitSummary,
    UnitFilter,
)

# Food models
from .food import (
    Food,
    FoodCreateRequest,
    FoodUpdateRequest,
    FoodSummary,
)

# Household models
from .household import (
    Household,
    HouseholdSummary,
)

# Label models
from .label import (
    Label,
    LabelCreateRequest,
    LabelUpdateRequest,
)


__all__ = [
    # Common
    "BaseModel",
    "RecipeVisibility",
    "UserRole", 
    "MealPlanType",
    "ShoppingListItemStatus",
    "RecipeScale",
    "TimeUnit",
    "OrderDirection",
    "Nutrition",
    "RecipeIngredient",
    "RecipeInstruction",
    "RecipeAsset",
    "RecipeSettings",
    "RecipeCategory",
    "RecipeTag",
    "RecipeTool",
    "PaginationInfo",
    "QueryFilter",
    "DateRange",
    "APIResponse",
    "ErrorDetail",
    "convert_datetime",
    "convert_date",
    "safe_get",
    "filter_none_values",
    
    # Recipe
    "Recipe",
    "RecipeCreateRequest",
    "RecipeUpdateRequest",
    "RecipeSummary",
    "RecipeFilter",
    "RecipeSuggestionsFilter",
    
    # User
    "User",
    "UserCreateRequest",
    "UserUpdateRequest", 
    "UserSummary",
    "UserFilter",
    
    # Group
    "Group",
    "GroupSummary",
    
    # Meal plan
    "MealPlan",
    "MealPlanCreateRequest",
    "MealPlanUpdateRequest",
    "MealPlanFilter",
    
    # Shopping list
    "ShoppingList",
    "ShoppingListCreateRequest",
    "ShoppingListUpdateRequest",
    "ShoppingListSummary",
    "ShoppingListFilter",
    
    # Shopping list item
    "ShoppingListItem",
    "ShoppingListItemCreateRequest",
    "ShoppingListItemUpdateRequest",

    # Unit
    "Unit",
    "UnitCreateRequest",
    "UnitUpdateRequest",
    "UnitSummary",
    "UnitFilter",
    
    # Food
    "Food",
    "FoodCreateRequest",
    "FoodUpdateRequest",
    "FoodSummary",
    
    # Household
    "Household",
    "HouseholdSummary",
    
    # Label
    "Label",
    "LabelCreateRequest",
    "LabelUpdateRequest",
] 