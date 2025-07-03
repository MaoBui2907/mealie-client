"""
Recipes endpoint manager for the Mealie SDK.

This module provides comprehensive recipe management functionality including
CRUD operations, searching, filtering, and recipe-specific features.
"""

from typing import Any, Dict, List, Optional, Union
from pathlib import Path

from ..models.recipe import (
    Recipe,
    RecipeCreateRequest,
    RecipeUpdateRequest,
    RecipeSummary,
    RecipeFilter,
    RecipeImportRequest,
    BulkRecipeExportRequest,
    RecipeImageRequest,
)
from ..exceptions import NotFoundError, ValidationError
from ..utils import build_url, clean_dict


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
        order_direction: str = "asc",
        search: Optional[str] = None,
        categories: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        tools: Optional[List[str]] = None,
        include_tags: bool = True,
    ) -> List[RecipeSummary]:
        """
        Get all recipes with optional filtering and pagination.

        Args:
            page: Page number (1-based)
            per_page: Number of recipes per page (max 100)
            order_by: Field to order by (name, date_added, etc.)
            order_direction: Order direction (asc or desc)
            search: Search term for recipe names and descriptions
            categories: List of category names to filter by
            tags: List of tag names to filter by
            tools: List of tool names to filter by
            include_tags: Whether to include tag information in response

        Returns:
            List of recipe summaries

        Raises:
            MealieAPIError: If the API request fails
        """
        recipe_filter = RecipeFilter(
            page=page,
            per_page=min(per_page, 100),  # Enforce API limit
            order_by=order_by,
            order_direction=order_direction,
            search=search,
            categories=categories,
            tags=tags,
            tools=tools,
            include_tags=include_tags,
        )

        response = await self.client.get("recipes", params=recipe_filter.to_params())
        
        # Handle both paginated and simple list responses
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
            return Recipe.from_dict(response) if isinstance(response, dict) else response
        except Exception as e:
            if hasattr(e, 'status_code') and e.status_code == 404:
                raise NotFoundError(
                    f"Recipe '{recipe_id_or_slug}' not found",
                    resource_type="recipe",
                    resource_id=recipe_id_or_slug,
                )
            raise

    async def create(self, recipe_data: Union[RecipeCreateRequest, Dict[str, Any]]) -> Recipe:
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

        # Clean the data to remove None values
        clean_data = clean_dict(data)

        response = await self.client.post("recipes", json_data=clean_data)
        return Recipe.from_dict(response) if isinstance(response, dict) else response

    async def update(
        self,
        recipe_id_or_slug: str,
        recipe_data: Union[RecipeUpdateRequest, Dict[str, Any]],
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

        # Clean the data to remove None values
        clean_data = clean_dict(data)

        try:
            response = await self.client.put(f"recipes/{recipe_id_or_slug}", json_data=clean_data)
            return Recipe.from_dict(response) if isinstance(response, dict) else response
        except Exception as e:
            if hasattr(e, 'status_code') and e.status_code == 404:
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
            if hasattr(e, 'status_code') and e.status_code == 404:
                raise NotFoundError(
                    f"Recipe '{recipe_id_or_slug}' not found",
                    resource_type="recipe",
                    resource_id=recipe_id_or_slug,
                )
            raise

    async def search(self, query: str, limit: int = 50) -> List[RecipeSummary]:
        """
        Search recipes by name, description, or ingredients.

        Args:
            query: Search query string
            limit: Maximum number of results to return

        Returns:
            List of matching recipe summaries
        """
        return await self.get_all(search=query, per_page=limit)

    async def get_by_category(self, category: str, limit: int = 50) -> List[RecipeSummary]:
        """
        Get recipes by category.

        Args:
            category: Category name or slug
            limit: Maximum number of results to return

        Returns:
            List of recipes in the category
        """
        return await self.get_all(categories=[category], per_page=limit)

    async def get_by_tag(self, tag: str, limit: int = 50) -> List[RecipeSummary]:
        """
        Get recipes by tag.

        Args:
            tag: Tag name or slug
            limit: Maximum number of results to return

        Returns:
            List of recipes with the tag
        """
        return await self.get_all(tags=[tag], per_page=limit)

    async def import_from_url(self, url: str, include_tags: bool = True) -> Recipe:
        """
        Import a recipe from a URL.

        Args:
            url: URL to import recipe from
            include_tags: Whether to include tags during import

        Returns:
            Imported recipe object

        Raises:
            ValidationError: If URL is invalid or import fails
            MealieAPIError: If the API request fails
        """
        import_request = RecipeImportRequest(url=url, include_tags=include_tags)
        
        response = await self.client.post(
            "recipes/create-url",
            json_data=import_request.to_dict()
        )
        return Recipe.from_dict(response) if isinstance(response, dict) else response

    async def get_image_url(self, recipe_id_or_slug: str, extension: str = "webp") -> str:
        """
        Get the URL for a recipe's image.

        Args:
            recipe_id_or_slug: Recipe ID or slug identifier
            extension: Image format (webp, jpg, png)

        Returns:
            Image URL
        """
        return build_url(
            self.client.base_url,
            f"recipes/{recipe_id_or_slug}/image",
            extension=extension
        )

    async def upload_image(
        self,
        recipe_id_or_slug: str,
        image_path: Union[str, Path],
        extension: str = "webp",
    ) -> Dict[str, Any]:
        """
        Upload an image for a recipe.

        Args:
            recipe_id_or_slug: Recipe ID or slug identifier
            image_path: Path to the image file
            extension: Image format for conversion

        Returns:
            Upload response data

        Raises:
            FileNotFoundError: If image file doesn't exist
            NotFoundError: If recipe not found
            MealieAPIError: If the API request fails
        """
        from ..utils import extract_file_info

        path = Path(image_path)
        if not path.exists():
            raise FileNotFoundError(f"Image file not found: {image_path}")

        file_info = extract_file_info(path)
        
        files = {
            "image": (file_info["name"], open(path, "rb"), file_info["mime_type"])
        }

        try:
            response = await self.client.put(
                f"recipes/{recipe_id_or_slug}/image",
                files=files,
                params={"extension": extension}
            )
            return response
        except Exception as e:
            if hasattr(e, 'status_code') and e.status_code == 404:
                raise NotFoundError(
                    f"Recipe '{recipe_id_or_slug}' not found",
                    resource_type="recipe",
                    resource_id=recipe_id_or_slug,
                )
            raise
        finally:
            # Close the file
            for file_tuple in files.values():
                if hasattr(file_tuple[1], 'close'):
                    file_tuple[1].close()

    async def delete_image(self, recipe_id_or_slug: str) -> bool:
        """
        Delete a recipe's image.

        Args:
            recipe_id_or_slug: Recipe ID or slug identifier

        Returns:
            True if deletion was successful

        Raises:
            NotFoundError: If recipe not found
            MealieAPIError: If the API request fails
        """
        try:
            await self.client.delete(f"recipes/{recipe_id_or_slug}/image")
            return True
        except Exception as e:
            if hasattr(e, 'status_code') and e.status_code == 404:
                raise NotFoundError(
                    f"Recipe '{recipe_id_or_slug}' not found",
                    resource_type="recipe",
                    resource_id=recipe_id_or_slug,
                )
            raise

    async def duplicate(self, recipe_id_or_slug: str, new_name: Optional[str] = None) -> Recipe:
        """
        Duplicate a recipe.

        Args:
            recipe_id_or_slug: Recipe ID or slug identifier
            new_name: Name for the duplicated recipe (optional)

        Returns:
            Duplicated recipe object

        Raises:
            NotFoundError: If recipe not found
            MealieAPIError: If the API request fails
        """
        # Get the original recipe
        original_recipe = await self.get(recipe_id_or_slug)
        
        # Prepare data for duplication
        duplicate_data = original_recipe.to_dict()
        
        # Remove fields that shouldn't be duplicated
        fields_to_remove = ["id", "slug", "date_added", "date_updated", "user_id"]
        for field in fields_to_remove:
            duplicate_data.pop(field, None)
        
        # Set new name if provided
        if new_name:
            duplicate_data["name"] = new_name
        else:
            duplicate_data["name"] = f"{original_recipe.name} (Copy)"
        
        # Create the duplicate
        return await self.create(duplicate_data)

    async def get_random(self, limit: int = 1) -> List[RecipeSummary]:
        """
        Get random recipes.

        Args:
            limit: Number of random recipes to return

        Returns:
            List of random recipe summaries
        """
        response = await self.client.get("recipes/random", params={"limit": limit})
        
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