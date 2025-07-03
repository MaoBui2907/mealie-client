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
    RecipeImportRequest,
    BulkRecipeExportRequest,
    RecipeImageRequest,
)

# User models
from .user import (
    User,
    UserCreateRequest,
    UserUpdateRequest,
    UserPasswordChangeRequest,
    UserPasswordResetRequest,
    UserSummary,
    UserFilter,
)

# Group models
from .group import (
    Group,
    GroupCreateRequest,
    GroupUpdateRequest,
    GroupSummary,
)

# Meal plan models
from .meal_plan import (
    MealPlan,
    MealPlanEntry,
    MealPlanCreateRequest,
    MealPlanUpdateRequest,
    MealPlanEntryCreateRequest,
    MealPlanFilter,
)

# Shopping list models
from .shopping_list import (
    ShoppingList,
    ShoppingListItem,
    ShoppingListCreateRequest,
    ShoppingListUpdateRequest,
    ShoppingListItemCreateRequest,
    ShoppingListItemUpdateRequest,
    ShoppingListSummary,
    ShoppingListFilter,
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
    "RecipeImportRequest",
    "BulkRecipeExportRequest",
    "RecipeImageRequest",
    
    # User
    "User",
    "UserCreateRequest",
    "UserUpdateRequest", 
    "UserPasswordChangeRequest",
    "UserPasswordResetRequest",
    "UserSummary",
    "UserFilter",
    
    # Group
    "Group",
    "GroupCreateRequest",
    "GroupUpdateRequest",
    "GroupSummary",
    
    # Meal plan
    "MealPlan",
    "MealPlanEntry",
    "MealPlanCreateRequest",
    "MealPlanUpdateRequest",
    "MealPlanEntryCreateRequest",
    "MealPlanFilter",
    
    # Shopping list
    "ShoppingList",
    "ShoppingListItem",
    "ShoppingListCreateRequest",
    "ShoppingListUpdateRequest",
    "ShoppingListItemCreateRequest",
    "ShoppingListItemUpdateRequest",
    "ShoppingListSummary",
    "ShoppingListFilter",
] 