"""
Integration tests for recipes endpoint.

Tests cover recipe CRUD operations, search functionality,
image management, and complex recipe workflows.
"""

import asyncio

import pytest
import httpx

from mealie_client.exceptions import NotFoundError, ValidationError


class TestRecipesCRUD:
    """Test suite for basic recipe CRUD operations."""

    @pytest.mark.integration
    async def test_get_all_recipes(self, integration_httpx_mock, authenticated_client, mock_pagination_response):
        """Test fetching all recipes with pagination."""
        integration_httpx_mock.get("/api/recipes").mock(
            return_value=httpx.Response(200, json=mock_pagination_response)
        )
        
        recipes = await authenticated_client.recipes.get_all()
        
        # get_all() returns List[RecipeSummary], not a dict with pagination info
        assert isinstance(recipes, list)
        assert len(recipes) == 10
        assert all(hasattr(recipe, 'id') for recipe in recipes)

    @pytest.mark.integration
    async def test_get_recipe_by_id(self, integration_httpx_mock, authenticated_client, mock_recipe_data):
        """Test fetching a specific recipe by ID."""
        recipe_id = "test-recipe-123"
        integration_httpx_mock.get(f"/api/recipes/{recipe_id}").mock(
            return_value=httpx.Response(200, json={
                "id": recipe_id,
                **mock_recipe_data
            })
        )
        
        recipe = await authenticated_client.recipes.get(recipe_id)
        
        # get() returns Recipe object, not dict
        assert recipe.id == recipe_id
        assert recipe.name == mock_recipe_data["name"]
        assert hasattr(recipe, 'recipe_ingredient')
        assert hasattr(recipe, 'recipe_instructions')

    @pytest.mark.integration
    async def test_get_recipe_not_found(self, integration_httpx_mock, authenticated_client):
        """Test handling of non-existent recipe."""
        recipe_id = "nonexistent-recipe"
        integration_httpx_mock.get(f"/api/recipes/{recipe_id}").mock(
            return_value=httpx.Response(404, json={"detail": "Recipe not found"})
        )
        
        with pytest.raises(NotFoundError) as exc_info:
            await authenticated_client.recipes.get(recipe_id)
        
        assert exc_info.value.status_code == 404

    @pytest.mark.integration
    async def test_create_recipe_success(self, integration_httpx_mock, authenticated_client, mock_recipe_data):
        """Test successful recipe creation."""
        created_recipe = {
            "id": "new-recipe-456",
            "slug": "integration-test-recipe",
            **mock_recipe_data
        }
        
        integration_httpx_mock.post("/api/recipes").mock(
            return_value=httpx.Response(201, json=created_recipe)
        )
        
        recipe = await authenticated_client.recipes.create(mock_recipe_data)
        
        # create() returns Recipe object, not dict
        assert recipe.id == "new-recipe-456"
        assert recipe.name == mock_recipe_data["name"]
        assert recipe.slug == "integration-test-recipe"

    @pytest.mark.integration
    async def test_create_recipe_validation_error(self, integration_httpx_mock, authenticated_client):
        """Test recipe creation with validation errors."""
        integration_httpx_mock.post("/api/recipes").mock(
            return_value=httpx.Response(422, json={
                "detail": [
                    {"loc": ["name"], "msg": "field required", "type": "value_error.missing"}
                ]
            })
        )
        
        with pytest.raises(ValidationError) as exc_info:
            await authenticated_client.recipes.create({})
        
        assert exc_info.value.status_code == 422
        assert "field required" in str(exc_info.value)

    @pytest.mark.integration
    async def test_update_recipe_success(self, integration_httpx_mock, authenticated_client, mock_recipe_data):
        """Test successful recipe update."""
        recipe_id = "update-recipe-789"
        updated_data = {**mock_recipe_data, "name": "Updated Recipe Name"}
        
        integration_httpx_mock.patch(f"/api/recipes/{recipe_id}").mock(
            return_value=httpx.Response(200, json={
                "id": recipe_id,
                **updated_data
            })
        )
        
        recipe = await authenticated_client.recipes.update(recipe_id, updated_data)
        
        assert recipe.id == recipe_id
        assert recipe.name == "Updated Recipe Name"

    @pytest.mark.integration
    async def test_delete_recipe_success(self, integration_httpx_mock, authenticated_client):
        """Test successful recipe deletion."""
        recipe_id = "delete-recipe-101"
        integration_httpx_mock.delete(f"/api/recipes/{recipe_id}").mock(
            return_value=httpx.Response(204)
        )
        
        # Should not raise any exceptions
        await authenticated_client.recipes.delete(recipe_id)

    @pytest.mark.integration
    async def test_delete_recipe_not_found(self, integration_httpx_mock, authenticated_client):
        """Test deletion of non-existent recipe."""
        recipe_id = "nonexistent-recipe"
        integration_httpx_mock.delete(f"/api/recipes/{recipe_id}").mock(
            return_value=httpx.Response(404, json={"detail": "Recipe not found"})
        )
        
        with pytest.raises(NotFoundError):
            await authenticated_client.recipes.delete(recipe_id)


class TestRecipeSearch:
    """Test suite for recipe search functionality."""

    @pytest.mark.integration
    async def test_search_recipes_with_filters(self, integration_httpx_mock, authenticated_client):
        """Test searching recipes with category and tag filters."""
        filtered_results = {
            "items": [
                {
                    "id": "1",
                    "name": "Vegetarian Pasta",
                    "recipe_category": [{"name": "Main Course"}],
                    "tags": [{"name": "vegetarian"}, {"name": "quick"}]
                }
            ],
            "page": 1,
            "per_page": 50,
            "total": 1
        }
        
        integration_httpx_mock.get("/api/recipes").mock(
            return_value=httpx.Response(200, json=filtered_results)
        )
        
        # search() method only takes query and limit, use get_all() for filters
        results = await authenticated_client.recipes.get_all(
            categories=["Main Course"],
            tags=["vegetarian"]
        )
        
        assert len(results) == 1
        recipe = results[0]
        # Note: RecipeSummary may not have full category/tag details
        assert hasattr(recipe, 'id')

    @pytest.mark.integration
    async def test_search_recipes_pagination(self, integration_httpx_mock, authenticated_client):
        """Test search with pagination parameters."""
        page2_results = {
            "items": [
                {"id": f"recipe_{i}", "name": f"Recipe {i}"} for i in range(51, 61)
            ],
            "page": 2,
            "per_page": 10,
            "total": 75
        }
        
        integration_httpx_mock.get("/api/recipes").mock(
            return_value=httpx.Response(200, json=page2_results)
        )
        
        results = await authenticated_client.recipes.get_all(page=2, per_page=10)
        
        assert len(results) == 10
