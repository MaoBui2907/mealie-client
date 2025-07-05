"""
E2E Recipes CRUD Tests

This module tests complete CRUD operations for recipes including
creation, reading, updating, deletion, and advanced features.
"""

import pytest
from mealie_client.exceptions import MealieAPIError, NotFoundError
from mealie_client.models.recipe import RecipeCreateRequest, RecipeUpdateRequest

from .utils import (
    assert_fields_not_none,
)


class TestE2ERecipesCRUD:
    """Test full CRUD operations for recipes."""

    @pytest.mark.asyncio
    async def test_basic_crud(self, e2e_test_base, sample_recipe_data):
        """Test basic CRUD operations for recipes."""
        client = e2e_test_base.client
        recipe = RecipeCreateRequest(**sample_recipe_data)

        all_recipes = await client.recipes.get_all(per_page=100)
        assert len(all_recipes) == 100

        # Create recipe
        created_recipe = await client.recipes.create(recipe)
        assert_fields_not_none(
            created_recipe, fields=["id", "name", "slug"]
        )

        # Update recipe
        updated_recipe = await client.recipes.update(created_recipe.id, RecipeUpdateRequest.from_dict(
            {
                "name": "Updated Recipe",
            }
        ))
        assert_fields_not_none(
            updated_recipe, fields=["id", "name", "slug"]
        )
        assert updated_recipe.name == "Updated Recipe"

        # Delete recipe
        await client.recipes.delete(updated_recipe.id)

        with pytest.raises(NotFoundError):
            await client.recipes.get(updated_recipe.id)

        # Import recipe from url
        url = "https://cookpad.com/vn/cong-thuc/12973110"
        imported_recipe_slug = await client.recipes.import_from_url(url)
        imported_recipe = await client.recipes.get(imported_recipe_slug)
        assert_fields_not_none(
            imported_recipe, fields=["id", "name", "slug", "org_url"]
        )
        assert imported_recipe.org_url == url

        # Delete imported recipe
        await client.recipes.delete(imported_recipe.id)

        with pytest.raises(NotFoundError):
            await client.recipes.get(imported_recipe.id)