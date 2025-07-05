"""
Unit tests for recipe models.

Tests cover Recipe model, request/response models, and recipe-related
data structures with validation and serialization.
"""

from datetime import datetime
from typing import Any, Dict, List

import pytest

from mealie_client.models.recipe import (
    Recipe,
    RecipeCreateRequest,
    RecipeUpdateRequest,
    RecipeSummary,
    RecipeFilter,
    RecipeSuggestionsFilter,
)
from mealie_client.models.common import (
    Nutrition,
    RecipeIngredient,
    RecipeInstruction,
    RecipeCategory,
    RecipeTag,
    RecipeTool,
    RecipeAsset,
    RecipeSettings,
)


class TestRecipe:
    """Test suite for Recipe model."""

    @pytest.mark.unit
    def test_init_with_defaults(self):
        """Test Recipe initialization with default values."""
        recipe = Recipe()
        
        assert recipe.id is None
        assert recipe.user_id is None
        assert recipe.group_id is None
        assert recipe.name == ""
        assert recipe.slug == ""
        assert recipe.image is None
        assert recipe.description is None
        assert recipe.recipe_yield is None
        assert recipe.recipe_ingredient == []
        assert recipe.recipe_instructions == []
        assert recipe.prep_time is None
        assert recipe.cook_time is None
        assert recipe.perform_time is None
        assert recipe.total_time is None
        assert recipe.recipe_category == []
        assert recipe.tags == []
        assert recipe.tools == []
        assert recipe.nutrition is None
        assert recipe.assets == []
        assert isinstance(recipe.settings, RecipeSettings)
        assert recipe.org_url is None
        assert recipe.rating is None
        assert recipe.recipe_yield is None
        assert recipe.date_added is None
        assert recipe.date_updated is None
        assert recipe.extras == {}

    @pytest.mark.unit
    def test_init_with_basic_fields(self):
        """Test Recipe initialization with basic fields."""
        recipe = Recipe(
            id="recipe-123",
            name="Chocolate Cake",
            slug="chocolate-cake",
            description="Delicious chocolate cake recipe"
        )
        
        assert recipe.id == "recipe-123"
        assert recipe.name == "Chocolate Cake"
        assert recipe.slug == "chocolate-cake"
        assert recipe.description == "Delicious chocolate cake recipe"

    @pytest.mark.unit
    def test_init_with_timing_fields(self):
        """Test Recipe initialization with timing fields."""
        recipe = Recipe(
            name="Quick Pasta",
            prep_time="PT15M",
            cook_time="PT10M",
            total_time="PT25M"
        )
        
        assert recipe.name == "Quick Pasta"
        assert recipe.prep_time == "PT15M"
        assert recipe.cook_time == "PT10M"
        assert recipe.total_time == "PT25M"

    @pytest.mark.unit
    def test_init_with_ingredients_and_instructions(self):
        """Test Recipe initialization with ingredients and instructions."""
        ingredients = [
            RecipeIngredient(title="Main", text="2 cups flour"),
            RecipeIngredient(title="Main", text="1 cup sugar")
        ]
        instructions = [
            RecipeInstruction(text="Mix dry ingredients"),
            RecipeInstruction(text="Add wet ingredients")
        ]
        
        recipe = Recipe(
            name="Simple Cake",
            recipe_ingredient=ingredients,
            recipe_instructions=instructions
        )
        
        assert recipe.name == "Simple Cake"
        assert len(recipe.recipe_ingredient) == 2
        assert len(recipe.recipe_instructions) == 2
        assert recipe.recipe_ingredient[0].text == "2 cups flour"
        assert recipe.recipe_instructions[0].text == "Mix dry ingredients"

    @pytest.mark.unit
    def test_init_with_categories_tags_tools(self):
        """Test Recipe initialization with categories, tags, and tools."""
        categories = [RecipeCategory(name="Dessert", slug="dessert")]
        tags = [RecipeTag(name="Sweet", slug="sweet")]
        tools = [RecipeTool(name="Mixer", slug="mixer")]
        
        recipe = Recipe(
            name="Dessert Recipe",
            recipe_category=categories,
            tags=tags,
            tools=tools
        )
        
        assert recipe.name == "Dessert Recipe"
        assert len(recipe.recipe_category) == 1
        assert len(recipe.tags) == 1
        assert len(recipe.tools) == 1
        assert recipe.recipe_category[0].name == "Dessert"
        assert recipe.tags[0].name == "Sweet"
        assert recipe.tools[0].name == "Mixer"

    @pytest.mark.unit
    def test_init_with_nutrition(self):
        """Test Recipe initialization with nutrition information."""
        nutrition = Nutrition(
            calories=350.0,
            protein_content=12.5,
            fat_content=15.2
        )
        
        recipe = Recipe(
            name="Healthy Bowl",
            nutrition=nutrition
        )
        
        assert recipe.name == "Healthy Bowl"
        assert recipe.nutrition == nutrition
        assert recipe.nutrition.calories == 350.0

    @pytest.mark.unit
    def test_init_with_assets(self):
        """Test Recipe initialization with assets."""
        assets = [
            RecipeAsset(name="Main Photo", file_name="main.jpg"),
            RecipeAsset(name="Step Photo", file_name="step1.jpg")
        ]
        
        recipe = Recipe(
            name="Photo Recipe",
            assets=assets
        )
        
        assert recipe.name == "Photo Recipe"
        assert len(recipe.assets) == 2
        assert recipe.assets[0].name == "Main Photo"

    @pytest.mark.unit
    def test_init_with_settings(self):
        """Test Recipe initialization with custom settings."""
        settings = RecipeSettings(
            public=True,
            show_nutrition=False,
            landscape_view=True
        )
        
        recipe = Recipe(
            name="Public Recipe",
            settings=settings
        )
        
        assert recipe.name == "Public Recipe"
        assert recipe.settings.public is True
        assert recipe.settings.show_nutrition is False

    @pytest.mark.unit
    def test_init_with_datetime_strings(self):
        """Test Recipe initialization with datetime strings."""
        recipe = Recipe(
            name="Dated Recipe",
            date_added="2023-12-25T14:30:45",
            date_updated="2023-12-26T10:15:30"
        )
        
        assert recipe.name == "Dated Recipe"
        assert isinstance(recipe.date_added, datetime)
        assert isinstance(recipe.date_updated, datetime)
        assert recipe.date_added.year == 2023
        assert recipe.date_added.month == 12
        assert recipe.date_added.day == 25

    @pytest.mark.unit
    def test_init_with_extras(self):
        """Test Recipe initialization with extra fields."""
        extras = {
            "custom_field": "custom_value",
            "difficulty": "medium",
            "source": "cookbook"
        }
        
        recipe = Recipe(
            name="Extended Recipe",
            extras=extras
        )
        
        assert recipe.name == "Extended Recipe"
        assert recipe.extras == extras
        assert recipe.extras["difficulty"] == "medium"

    @pytest.mark.unit
    def test_from_dict_handles_existing_objects(self):
        """Test Recipe.from_dict handles already instantiated objects."""
        ingredient = RecipeIngredient(title="Main", text="2 cups flour")
        instruction = RecipeInstruction(text="Mix ingredients")
        
        data = {
            "name": "Mixed Recipe",
            "recipe_ingredient": [ingredient],
            "recipe_instructions": [instruction]
        }
        
        recipe = Recipe.from_dict(data)
        
        assert recipe.name == "Mixed Recipe"
        assert len(recipe.recipe_ingredient) == 1
        assert recipe.recipe_ingredient[0] == ingredient
        assert recipe.recipe_instructions[0] == instruction

    @pytest.mark.unit
    def test_to_dict_serialization(self):
        """Test Recipe to_dict serialization."""
        recipe = Recipe(
            name="Serialize Test",
            prep_time="PT15M",
            rating=4.5,
            date_added=datetime(2023, 12, 25, 14, 30, 45)
        )
        
        result = recipe.to_dict()
        
        assert result["name"] == "Serialize Test"
        assert result["prepTime"] == "PT15M"
        assert result["rating"] == 4.5
        assert result["dateAdded"] == "2023-12-25T14:30:45"


class TestRecipeCreateRequest:
    """Test suite for RecipeCreateRequest model."""

    @pytest.mark.unit
    def test_init_with_required_fields(self):
        """Test RecipeCreateRequest initialization with required fields."""
        request = RecipeCreateRequest(name="New Recipe")
        
        assert request.name == "New Recipe"

    @pytest.mark.unit
    def test_init_with_all_fields(self):
        """Test RecipeCreateRequest initialization with all fields."""
        request = RecipeCreateRequest(
            name="Complete Recipe",
            description="A complete recipe description"
        )
        
        assert request.name == "Complete Recipe"

    @pytest.mark.unit
    def test_to_dict(self):
        """Test RecipeCreateRequest to_dict conversion."""
        request = RecipeCreateRequest(
            name="Dict Recipe",
        )
        result = request.to_dict()
        
        expected = {
            "name": "Dict Recipe",
        }
        assert result == expected

    @pytest.mark.unit
    def test_from_dict(self):
        """Test RecipeCreateRequest from_dict creation."""
        data = {
            "name": "From Dict Recipe",
            "description": "Created from dictionary"
        }
        request = RecipeCreateRequest.from_dict(data)
        
        assert isinstance(request, RecipeCreateRequest)
        assert request.name == "From Dict Recipe"


class TestRecipeUpdateRequest:
    """Test suite for RecipeUpdateRequest model."""

    @pytest.mark.unit
    def test_init_with_defaults(self):
        """Test RecipeUpdateRequest initialization with defaults."""
        request = RecipeUpdateRequest()
        
        assert request.name == ''

    @pytest.mark.unit
    def test_init_with_fields(self):
        """Test RecipeUpdateRequest initialization with fields."""
        request = RecipeUpdateRequest(
            name="Updated Recipe",
            description="Updated description"
        )
        
        assert request.name == "Updated Recipe"
        assert request.description == "Updated description"

    @pytest.mark.unit
    def test_partial_updates(self):
        """Test RecipeUpdateRequest supports partial updates."""
        # Test updating only name
        request1 = RecipeUpdateRequest(name="New Name")
        assert request1.name == "New Name"
        
class TestRecipeSummary:
    """Test suite for RecipeSummary model."""

    @pytest.mark.unit
    def test_init_with_defaults(self):
        """Test RecipeSummary initialization with defaults."""
        summary = RecipeSummary()
        
        assert summary.id is None
        assert summary.name == ""
        assert summary.slug == ""
        assert summary.image is None

    @pytest.mark.unit
    def test_init_with_fields(self):
        """Test RecipeSummary initialization with fields."""
        summary = RecipeSummary(
            id="summary-123",
            name="Summary Recipe",
            slug="summary-recipe",
            image="summary.jpg"
        )
        
        assert summary.id == "summary-123"
        assert summary.name == "Summary Recipe"
        assert summary.slug == "summary-recipe"
        assert summary.image == "summary.jpg"


class TestRecipeFilter:
    """Test suite for RecipeFilter model."""

    @pytest.mark.unit
    def test_init_with_defaults(self):
        """Test RecipeFilter initialization with defaults."""
        filter_obj = RecipeFilter()
        
        assert filter_obj.page == 1
        assert filter_obj.per_page == 50
        assert filter_obj.search is None

    @pytest.mark.unit
    def test_init_with_custom_values(self):
        """Test RecipeFilter initialization with custom values."""
        filter_obj = RecipeFilter(
            page=2,
            per_page=25,
            search="chocolate"
        )
        
        assert filter_obj.page == 2
        assert filter_obj.per_page == 25
        assert filter_obj.search == "chocolate"

    @pytest.mark.unit
    def test_inherits_from_base_filter(self):
        """Test that RecipeFilter inherits from base filter functionality."""
        filter_obj = RecipeFilter(page=3, search="pasta")
        
        # Should have pagination fields
        assert hasattr(filter_obj, 'page')
        assert hasattr(filter_obj, 'per_page')
        assert filter_obj.page == 3