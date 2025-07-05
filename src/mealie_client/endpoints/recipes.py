"""
Recipes endpoint manager for the Mealie SDK.

This module provides comprehensive recipe management functionality including
CRUD operations, searching, filtering, and recipe-specific features.
"""

from typing import Any, List, Optional

from mealie_client.models.common import OrderDirection, OrderByNullPosition

from ..models.recipe import (
    Recipe,
    RecipeCreateRequest,
    RecipeUpdateRequest,
    RecipeSummary,
    RecipeFilter,
    RecipeParseRequest,
    RecipeSuggestionsFilter,
)
from ..exceptions import NotFoundError
from ..utils import clean_dict


class RecipesManager:
    """
    Manages recipe-related API operations.
    
    Provides methods for creating, reading, updating, and deleting recipes,
    as well as advanced features like recipe import, export, and image management.
    """

    def __init__(self, client: Any) -> None:
        """
        Initialize the recipes manager.

        Args:
            client: The MealieClient instance
        """
        self.client = client

    async def get_all(
        self,
        page: int = 1,
        per_page: int = 50,
        order_by: Optional[str] = None,
        order_direction: OrderDirection = OrderDirection.ASC,
        order_by_null_position: OrderByNullPosition = OrderByNullPosition.LAST,
        search: Optional[str] = None,
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
    ) -> List[RecipeSummary]:
        """
        Get all recipes with optional filtering and pagination.

        Args:
            page: Page number (1-based)
            per_page: Number of recipes per page (max 100)
            order_by: Field to order by (name, date_added, etc.)
            order_direction: Order direction (asc or desc)
            order_by_null_position: Position of null values in ordering
            search: Search term for recipe names and descriptions
            categories: List of category names to filter by
            tags: List of tag names to filter by
            tools: List of tool names to filter by
            foods: List of food names to filter by
            households: List of household names to filter by
            cookbook: Name of cookbook to filter by
            require_all_categories: Whether to require all categories to be present
            require_all_tags: Whether to require all tags to be present
            require_all_tools: Whether to require all tools to be present
            require_all_foods: Whether to require all foods to be present

        Returns:
            List of recipe summaries

        Raises:
            MealieAPIError: If the API request fails
        """
        recipe_filter = RecipeFilter(
            page=page,
            per_page=min(per_page, 100),
            order_by=order_by,
            order_direction=order_direction,
            order_by_null_position=order_by_null_position,
            search=search,
            categories=categories,
            tags=tags,
            tools=tools,
            foods=foods,
            households=households,
            cookbook=cookbook,
            require_all_categories=require_all_categories,
            require_all_tags=require_all_tags,
            require_all_tools=require_all_tools,
            require_all_foods=require_all_foods,
        )

        response = await self.client.get("recipes", params=recipe_filter.to_params())
        
        if isinstance(response, dict) and "items" in response:
            recipes_data = response["items"]
        elif isinstance(response, list):
            recipes_data = response
        else:
            recipes_data = []

        return [
            RecipeSummary.from_dict(recipe_data) if isinstance(recipe_data, dict) else recipe_data
            for recipe_data in recipes_data
        ]

    async def get(self, recipe_id_or_slug: str) -> Recipe:
        """
        Get a specific recipe by ID or slug.

        Args:
            recipe_id_or_slug: Recipe ID or slug identifier

        Returns:
            Complete recipe object

        Raises:
            NotFoundError: If recipe not found
            MealieAPIError: If the API request fails
        """
        try:
            response = await self.client.get(f"recipes/{recipe_id_or_slug}")
            if not isinstance(response, dict):
                raise ValueError("Response must be a dictionary")
            
            return Recipe.from_dict(response)
        except Exception as e:
            if hasattr(e, 'status_code') and getattr(e, 'status_code') == 404:
                raise NotFoundError(
                    f"Recipe '{recipe_id_or_slug}' not found",
                    resource_type="recipe",
                    resource_id=recipe_id_or_slug,
                )
            raise

    async def create(self, recipe_data: RecipeCreateRequest) -> Recipe:
        """
        Create a new recipe.

        Args:
            recipe_data: Recipe creation data

        Returns:
            Created recipe object

        Raises:
            ValidationError: If recipe data is invalid
            MealieAPIError: If the API request fails
        """
        if isinstance(recipe_data, RecipeCreateRequest):
            data = recipe_data.to_dict()
        else:
            data = recipe_data

        response = await self.client.post("recipes", json_data=data)
        
        # Handle different response types
        if isinstance(response, dict):
            return Recipe.from_dict(response)
        elif isinstance(response, str):
            # If response is a string (possibly recipe ID), create minimal Recipe object
            return Recipe(id=response, name=data.get('name', ''), slug=data.get('slug', ''))
        else:
            # For other response types, try to convert to Recipe
            return response

    async def update(
        self,
        recipe_id_or_slug: str,
        recipe_data: RecipeUpdateRequest,
    ) -> Recipe:
        """
        Update an existing recipe.

        Args:
            recipe_id_or_slug: Recipe ID or slug identifier
            recipe_data: Recipe update data

        Returns:
            Updated recipe object

        Raises:
            NotFoundError: If recipe not found
            ValidationError: If recipe data is invalid
            MealieAPIError: If the API request fails
        """
        if isinstance(recipe_data, RecipeUpdateRequest):
            data = recipe_data.to_dict()
        else:
            data = recipe_data

        try:
            response = await self.client.patch(f"recipes/{recipe_id_or_slug}", json_data=clean_dict(data))
            
            # Handle different response types
            if isinstance(response, dict):
                return Recipe.from_dict(response)
            elif isinstance(response, str):
                # If response is a string (possibly recipe ID), create minimal Recipe object
                return Recipe(id=response, name=data.get('name', ''), slug=data.get('slug', ''))
            else:
                # For other response types, try to convert to Recipe
                return response
        except Exception as e:
            if hasattr(e, 'status_code') and getattr(e, 'status_code') == 404:
                raise NotFoundError(
                    f"Recipe '{recipe_id_or_slug}' not found",
                    resource_type="recipe",
                    resource_id=recipe_id_or_slug,
                )
            raise

    async def delete(self, recipe_id_or_slug: str) -> bool:
        """
        Delete a recipe.

        Args:
            recipe_id_or_slug: Recipe ID or slug identifier

        Returns:
            True if deletion was successful

        Raises:
            NotFoundError: If recipe not found
            MealieAPIError: If the API request fails
        """
        try:
            await self.client.delete(f"recipes/{recipe_id_or_slug}")
            return True
        except Exception as e:
            if hasattr(e, 'status_code') and getattr(e, 'status_code') == 404:
                raise NotFoundError(
                    f"Recipe '{recipe_id_or_slug}' not found",
                    resource_type="recipe",
                    resource_id=recipe_id_or_slug,
                )
            raise

    async def import_from_url(self, url: str, include_tags: bool = True) -> str:
        """
        Import a recipe from a URL.

        Args:
            url: URL to import recipe from
            include_tags: Whether to include tags during import

        Returns:
            Imported recipe slug

        Raises:
            ValidationError: If URL is invalid or import fails
            MealieAPIError: If the API request fails
        """
        import_request = RecipeParseRequest(url=url, include_tags=include_tags)
        
        response = await self.client.post(
            "recipes/create/url",
            json_data=import_request.to_dict()
        )
        return response if isinstance(response, str) else response.get("slug", "")

    async def get_suggestions(self,
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
    ) -> List[RecipeSummary]:
        """
        Get suggestions for recipes.

        Args:
            limit: Number of suggestions to return
            tools: List of tool names to filter by
            foods: List of food names to filter by
            order_by: Field to order by
            order_direction: Order direction
            order_by_null_position: Position of null values in ordering
            max_missing_foods: Maximum number of missing foods
            max_missing_tools: Maximum number of missing tools
            include_foods_on_hand: Whether to include foods on hand
            include_tools_on_hand: Whether to include tools on hand
            accept_language: Accept language

        Returns:
            List of recipe summaries
        """
        response = await self.client.get("recipes/suggestions", params=RecipeSuggestionsFilter(
            limit=limit,
            tools=tools,
            foods=foods,
            order_by=order_by,
            order_direction=order_direction,
            order_by_null_position=order_by_null_position,
            max_missing_foods=max_missing_foods,
            max_missing_tools=max_missing_tools,
            include_foods_on_hand=include_foods_on_hand,
            include_tools_on_hand=include_tools_on_hand,
            accept_language=accept_language,
            **kwargs,
        ).to_params())
        
        if isinstance(response, list):
            recipes_data = response
        elif isinstance(response, dict) and "items" in response:
            recipes_data = response["items"]
        else:
            recipes_data = [response] if response else []

        return [
            RecipeSummary.from_dict(recipe_data) if isinstance(recipe_data, dict) else recipe_data
            for recipe_data in recipes_data
        ] 