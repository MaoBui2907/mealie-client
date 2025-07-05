"""
Recipe models for the Mealie SDK.

This module contains data models for recipes, including ingredients,
instructions, nutrition information, and recipe metadata.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from .common import (
    BaseModel,
    Nutrition,
    OrderByNullPosition,
    OrderDirection,
    QueryFilter,
    RecipeAsset,
    RecipeCategory,
    RecipeIngredient,
    RecipeInstruction,
    RecipeSettings,
    RecipeTag,
    RecipeTool,
    convert_datetime,
)


class Recipe(BaseModel):
    """
    Complete recipe model with all fields and metadata.
    """

    def __init__(
        self,
        # Core fields
        id: Optional[str] = None,
        user_id: Optional[str] = None,
        group_id: Optional[str] = None,
        household_id: Optional[str] = None,
        name: str = "",
        slug: str = "",
        image: Optional[str] = None,
        recipe_servings: Optional[int] = None,
        recipe_yield_quantity: Optional[float] = None,
        recipe_yield: Optional[str] = None,
        total_time: Optional[str] = None,
        prep_time: Optional[str] = None,
        cook_time: Optional[str] = None,
        perform_time: Optional[str] = None,
        description: Optional[str] = None,
        recipe_category: Optional[List[RecipeCategory]] = None,
        tags: Optional[List[RecipeTag]] = None,
        tools: Optional[List[RecipeTool]] = None,
        rating: Optional[float] = None,
        org_url: Optional[str] = None,
        recipe_ingredient: Optional[List[RecipeIngredient]] = None,
        recipe_instructions: Optional[List[RecipeInstruction]] = None,
        nutrition: Optional[Nutrition] = None,
        assets: Optional[List[RecipeAsset]] = None,
        settings: Optional[RecipeSettings] = None,
        date_added: Optional[Union[str, datetime]] = None,
        date_updated: Optional[Union[str, datetime]] = None,
        created_at: Optional[Union[str, datetime]] = None,
        updated_at: Optional[Union[str, datetime]] = None,
        last_made: Optional[Union[str, datetime]] = None,
        extras: Optional[Dict[str, Any]] = None,
        notes: Optional[List[str]] = None,
        comments: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> None:
        self.id = id
        self.user_id = user_id
        self.group_id = group_id
        self.household_id = household_id
        self.name = name
        self.slug = slug
        self.image = image
        self.recipe_servings = recipe_servings
        self.recipe_yield_quantity = recipe_yield_quantity
        self.recipe_yield = recipe_yield
        self.total_time = total_time
        self.prep_time = prep_time
        self.cook_time = cook_time
        self.perform_time = perform_time
        self.description = description
        self.recipe_category = recipe_category or []
        self.tags = tags or []
        self.tools = tools or []
        self.rating = rating
        self.org_url = org_url
        self.recipe_ingredient = recipe_ingredient or []
        self.recipe_instructions = recipe_instructions or []
        self.nutrition = nutrition
        self.assets = assets or []
        self.settings = settings or RecipeSettings()
        self.date_added = convert_datetime(date_added)
        self.date_updated = convert_datetime(date_updated)
        self.created_at = convert_datetime(created_at)
        self.updated_at = convert_datetime(updated_at)
        self.last_made = convert_datetime(last_made)
        self.extras = extras or {}
        self.notes = notes or []
        self.comments = comments or []
        super().__init__(**kwargs)

class RecipeCreateRequest(BaseModel):
    """Request model for creating a new recipe."""

    def __init__(
        self,
        name: str,
        **kwargs: Any,
    ) -> None:
        self.name = name
        super().__init__(**kwargs)


class RecipeUpdateRequest(BaseModel):
    """Request model for updating an existing recipe."""

    def __init__(
        self,
        # Core fields
        id: Optional[str] = None,
        user_id: Optional[str] = None,
        group_id: Optional[str] = None,
        household_id: Optional[str] = None,
        name: str = "",
        slug: str = "",
        image: Optional[str] = None,
        recipe_servings: Optional[int] = None,
        recipe_yield_quantity: Optional[float] = None,
        recipe_yield: Optional[str] = None,
        total_time: Optional[str] = None,
        prep_time: Optional[str] = None,
        cook_time: Optional[str] = None,
        perform_time: Optional[str] = None,
        description: Optional[str] = None,
        recipe_category: Optional[List[RecipeCategory]] = None,
        tags: Optional[List[RecipeTag]] = None,
        tools: Optional[List[RecipeTool]] = None,
        rating: Optional[float] = None,
        org_url: Optional[str] = None,
        recipe_ingredient: Optional[List[RecipeIngredient]] = None,
        recipe_instructions: Optional[List[RecipeInstruction]] = None,
        nutrition: Optional[Nutrition] = None,
        assets: Optional[List[RecipeAsset]] = None,
        settings: Optional[RecipeSettings] = None,
        date_added: Optional[Union[str, datetime]] = None,
        date_updated: Optional[Union[str, datetime]] = None,
        created_at: Optional[Union[str, datetime]] = None,
        updated_at: Optional[Union[str, datetime]] = None,
        last_made: Optional[Union[str, datetime]] = None,
        extras: Optional[Dict[str, Any]] = None,
        notes: Optional[List[str]] = None,
        comments: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> None:
        self.id = id
        self.user_id = user_id
        self.group_id = group_id
        self.household_id = household_id
        self.name = name
        self.slug = slug
        self.image = image
        self.recipe_servings = recipe_servings
        self.recipe_yield_quantity = recipe_yield_quantity
        self.recipe_yield = recipe_yield
        self.total_time = total_time
        self.prep_time = prep_time
        self.cook_time = cook_time
        self.perform_time = perform_time
        self.description = description
        self.recipe_category = recipe_category or []
        self.tags = tags or []
        self.tools = tools or []
        self.rating = rating
        self.org_url = org_url
        self.recipe_ingredient = recipe_ingredient or []
        self.recipe_instructions = recipe_instructions or []
        self.nutrition = nutrition
        self.assets = assets or []
        self.settings = settings or RecipeSettings()
        self.date_added = convert_datetime(date_added)
        self.date_updated = convert_datetime(date_updated)
        self.created_at = convert_datetime(created_at)
        self.updated_at = convert_datetime(updated_at)
        self.last_made = convert_datetime(last_made)
        self.extras = extras or {}
        self.notes = notes or []
        self.comments = comments or []
        super().__init__(**kwargs)


class RecipeParseRequest(BaseModel):
    """Request model for parsing a recipe from a URL, HTML, Text, or Image."""

    def __init__(
        self,
        url: Optional[str] = None,
        data: Optional[str] = None,
        image: Optional[str] = None,
        file: Optional[str] = None,
        include_tags: bool = True,
        **kwargs: Any,
    ) -> None:
        self.url = url
        self.data = data
        self.image = image
        self.file = file
        self.include_tags = include_tags
        super().__init__(**kwargs)

class RecipeSummary(BaseModel):
    """Lightweight recipe summary for list views."""

    def __init__(
        self,
        id: Optional[str] = None,
        user_id: Optional[str] = None,
        group_id: Optional[str] = None,
        household_id: Optional[str] = None,
        name: str = "",
        slug: str = "",
        image: Optional[str] = None,
        recipe_servings: Optional[int] = None,
        recipe_yield_quantity: Optional[float] = None,
        recipe_yield: Optional[str] = None,
        total_time: Optional[str] = None,
        prep_time: Optional[str] = None,
        cook_time: Optional[str] = None,
        perform_time: Optional[str] = None,
        description: Optional[str] = None,
        recipe_category: Optional[List[RecipeCategory]] = None,
        tags: Optional[List[RecipeTag]] = None,
        tools: Optional[List[RecipeTool]] = None,
        rating: Optional[float] = None,
        org_url: Optional[str] = None,
        date_added: Optional[Union[str, datetime]] = None,
        date_updated: Optional[Union[str, datetime]] = None,
        created_at: Optional[Union[str, datetime]] = None,
        updated_at: Optional[Union[str, datetime]] = None,
        last_made: Optional[Union[str, datetime]] = None,
        **kwargs: Any,
    ) -> None:
        self.id = id
        self.user_id = user_id
        self.group_id = group_id
        self.household_id = household_id
        self.name = name
        self.slug = slug
        self.image = image
        self.recipe_servings = recipe_servings
        self.recipe_yield_quantity = recipe_yield_quantity
        self.recipe_yield = recipe_yield
        self.total_time = total_time
        self.prep_time = prep_time
        self.cook_time = cook_time
        self.perform_time = perform_time
        self.description = description
        self.recipe_category = recipe_category or []
        self.tags = tags or []
        self.tools = tools or []
        self.rating = rating
        self.org_url = org_url
        self.date_added = convert_datetime(date_added)
        self.date_updated = convert_datetime(date_updated)
        self.created_at = convert_datetime(created_at)
        self.updated_at = convert_datetime(updated_at)
        self.last_made = convert_datetime(last_made)
        super().__init__(**kwargs)


class RecipeFilter(QueryFilter):
    """Filter options for recipe queries."""

    def __init__(
        self,
        page: int = 1,
        per_page: int = 50,
        order_by: Optional[str] = None,
        order_direction: OrderDirection = OrderDirection.ASC,
        order_by_null_position: OrderByNullPosition = OrderByNullPosition.LAST,
        search: Optional[str] = None,
        accept_language: Optional[str] = None,
        # Recipe-specific filters
        categories: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        tools: Optional[List[str]] = None,
        foods: Optional[List[str]] = None,
        households: Optional[List[str]] = None,
        cookbook: Optional[str] = None,
        require_all_categories: bool = False,
        require_all_tags: bool = False,
        require_all_tools: bool = False,
        require_all_foods: bool = False,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            page=page,
            per_page=per_page,
            order_by=order_by,
            order_direction=order_direction,
            order_by_null_position=order_by_null_position,
            search=search,
            accept_language=accept_language,
            **kwargs,
        )
        self.categories = categories or []
        self.tags = tags or []
        self.tools = tools or []
        self.foods = foods or []
        self.households = households or []
        self.cookbook = cookbook
        self.require_all_categories = require_all_categories
        self.require_all_tags = require_all_tags
        self.require_all_tools = require_all_tools
        self.require_all_foods = require_all_foods

    def to_params(self) -> Dict[str, Any]:
        """Convert filter to query parameters."""
        # Get base parameters
        params = super().to_params()
        
        # Add recipe-specific parameters
        if self.categories:
            params["categories"] = ",".join(self.categories)
        if self.tags:
            params["tags"] = ",".join(self.tags)
        if self.tools:
            params["tools"] = ",".join(self.tools)
        if self.foods:
            params["foods"] = ",".join(self.foods)
        if self.households:
            params["households"] = ",".join(self.households)
        if self.cookbook:
            params["cookbook"] = self.cookbook
        if self.require_all_categories:
            params["requireAllCategories"] = "true"
        if self.require_all_tags:
            params["requireAllTags"] = "true"
        if self.require_all_tools:
            params["requireAllTools"] = "true"
        if self.require_all_foods:
            params["requireAllFoods"] = "true"
            
        return params

class RecipeSuggestionsFilter(QueryFilter):
    def __init__(
        self,
        page: int = 1,
        per_page: int = 50,
        limit: int = 1,
        tools: Optional[List[str]] = None,
        foods: Optional[List[str]] = None,
        order_by: Optional[str] = None,
        order_direction: OrderDirection = OrderDirection.ASC,
        order_by_null_position: OrderByNullPosition = OrderByNullPosition.LAST,
        max_missing_foods: int = 0,
        max_missing_tools: int = 0,
        include_foods_on_hand: bool = True,
        include_tools_on_hand: bool = True,
        accept_language: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            page=page,
            per_page=per_page,
            order_by=order_by,
            order_direction=order_direction,
            order_by_null_position=order_by_null_position,
            accept_language=accept_language,
            **kwargs,
        )
        self.limit = limit
        self.tools = tools or []
        self.foods = foods or []
        self.max_missing_foods = max_missing_foods
        self.max_missing_tools = max_missing_tools
        self.include_foods_on_hand = include_foods_on_hand
        self.include_tools_on_hand = include_tools_on_hand

    def to_params(self) -> Dict[str, Any]:
        params = super().to_params()
        if self.limit:
            params["limit"] = self.limit
        if self.tools:
            params["tools"] = ",".join(self.tools)
        if self.foods:
            params["foods"] = ",".join(self.foods)
        if self.max_missing_foods:
            params["maxMissingFoods"] = self.max_missing_foods
        if self.max_missing_tools:
            params["maxMissingTools"] = self.max_missing_tools
        if self.include_foods_on_hand:
            params["includeFoodsOnHand"] = "true"
        if self.include_tools_on_hand:
            params["includeToolsOnHand"] = "true"
        return params


