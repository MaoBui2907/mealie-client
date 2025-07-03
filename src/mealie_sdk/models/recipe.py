"""
Recipe models for the Mealie SDK.

This module contains data models for recipes, including ingredients,
instructions, nutrition information, and recipe metadata.
"""

from datetime import datetime, date
from typing import Any, Dict, List, Optional, Union

from .common import (
    BaseModel,
    Nutrition,
    RecipeAsset,
    RecipeCategory,
    RecipeIngredient,
    RecipeInstruction,
    RecipeSettings,
    RecipeTag,
    RecipeTool,
    RecipeVisibility,
    convert_datetime,
    convert_date,
    safe_get,
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
        name: str = "",
        slug: str = "",
        image: Optional[str] = None,
        
        # Recipe content
        description: Optional[str] = None,
        recipe_yield: Optional[str] = None,
        recipe_ingredient: Optional[List[RecipeIngredient]] = None,
        recipe_instructions: Optional[List[RecipeInstruction]] = None,
        
        # Timing
        prep_time: Optional[str] = None,
        cook_time: Optional[str] = None,
        perform_time: Optional[str] = None,
        total_time: Optional[str] = None,
        
        # Classification
        recipe_category: Optional[List[RecipeCategory]] = None,
        tags: Optional[List[RecipeTag]] = None,
        tools: Optional[List[RecipeTool]] = None,
        
        # Nutrition
        nutrition: Optional[Nutrition] = None,
        
        # Assets and media
        assets: Optional[List[RecipeAsset]] = None,
        
        # Settings and visibility
        settings: Optional[RecipeSettings] = None,
        org_url: Optional[str] = None,
        
        # Metadata
        rating: Optional[float] = None,
        recipe_yield_quantity: Optional[float] = None,
        recipe_yield_unit: Optional[str] = None,
        
        # Timestamps
        date_added: Optional[Union[str, datetime]] = None,
        date_updated: Optional[Union[str, datetime]] = None,
        
        # Extra fields
        extras: Optional[Dict[str, Any]] = None,
        
        **kwargs: Any,
    ) -> None:
        # Core fields
        self.id = id
        self.user_id = user_id
        self.group_id = group_id
        self.name = name
        self.slug = slug
        self.image = image
        
        # Recipe content
        self.description = description
        self.recipe_yield = recipe_yield
        self.recipe_ingredient = recipe_ingredient or []
        self.recipe_instructions = recipe_instructions or []
        
        # Timing
        self.prep_time = prep_time
        self.cook_time = cook_time
        self.perform_time = perform_time
        self.total_time = total_time
        
        # Classification
        self.recipe_category = recipe_category or []
        self.tags = tags or []
        self.tools = tools or []
        
        # Nutrition
        self.nutrition = nutrition
        
        # Assets and media
        self.assets = assets or []
        
        # Settings and visibility
        self.settings = settings or RecipeSettings()
        self.org_url = org_url
        
        # Metadata
        self.rating = rating
        self.recipe_yield_quantity = recipe_yield_quantity
        self.recipe_yield_unit = recipe_yield_unit
        
        # Timestamps
        self.date_added = convert_datetime(date_added)
        self.date_updated = convert_datetime(date_updated)
        
        # Extra fields
        self.extras = extras or {}
        
        super().__init__(**kwargs)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Recipe":
        """Create a Recipe instance from a dictionary."""
        # Handle nested objects
        recipe_data = data.copy()
        
        # Convert ingredients
        if "recipe_ingredient" in recipe_data and recipe_data["recipe_ingredient"]:
            recipe_data["recipe_ingredient"] = [
                RecipeIngredient.from_dict(ing) if isinstance(ing, dict) else ing
                for ing in recipe_data["recipe_ingredient"]
            ]
        
        # Convert instructions
        if "recipe_instructions" in recipe_data and recipe_data["recipe_instructions"]:
            recipe_data["recipe_instructions"] = [
                RecipeInstruction.from_dict(inst) if isinstance(inst, dict) else inst
                for inst in recipe_data["recipe_instructions"]
            ]
        
        # Convert categories
        if "recipe_category" in recipe_data and recipe_data["recipe_category"]:
            recipe_data["recipe_category"] = [
                RecipeCategory.from_dict(cat) if isinstance(cat, dict) else cat
                for cat in recipe_data["recipe_category"]
            ]
        
        # Convert tags
        if "tags" in recipe_data and recipe_data["tags"]:
            recipe_data["tags"] = [
                RecipeTag.from_dict(tag) if isinstance(tag, dict) else tag
                for tag in recipe_data["tags"]
            ]
        
        # Convert tools
        if "tools" in recipe_data and recipe_data["tools"]:
            recipe_data["tools"] = [
                RecipeTool.from_dict(tool) if isinstance(tool, dict) else tool
                for tool in recipe_data["tools"]
            ]
        
        # Convert assets
        if "assets" in recipe_data and recipe_data["assets"]:
            recipe_data["assets"] = [
                RecipeAsset.from_dict(asset) if isinstance(asset, dict) else asset
                for asset in recipe_data["assets"]
            ]
        
        # Convert nutrition
        if "nutrition" in recipe_data and recipe_data["nutrition"]:
            if isinstance(recipe_data["nutrition"], dict):
                recipe_data["nutrition"] = Nutrition.from_dict(recipe_data["nutrition"])
        
        # Convert settings
        if "settings" in recipe_data and recipe_data["settings"]:
            if isinstance(recipe_data["settings"], dict):
                recipe_data["settings"] = RecipeSettings.from_dict(recipe_data["settings"])
        
        return cls(**recipe_data)

    def get_total_time_minutes(self) -> Optional[int]:
        """Get total time in minutes."""
        if not self.total_time:
            return None
        
        # Parse ISO 8601 duration format (PT30M, PT1H30M, etc.)
        from ..utils import parse_duration
        return parse_duration(self.total_time)

    def get_prep_time_minutes(self) -> Optional[int]:
        """Get prep time in minutes."""
        if not self.prep_time:
            return None
        
        from ..utils import parse_duration
        return parse_duration(self.prep_time)

    def get_cook_time_minutes(self) -> Optional[int]:
        """Get cook time in minutes."""
        if not self.cook_time:
            return None
        
        from ..utils import parse_duration
        return parse_duration(self.cook_time)

    def is_public(self) -> bool:
        """Check if recipe is public."""
        return self.settings.public if self.settings else False

    def get_category_names(self) -> List[str]:
        """Get list of category names."""
        return [cat.name for cat in self.recipe_category]

    def get_tag_names(self) -> List[str]:
        """Get list of tag names."""
        return [tag.name for tag in self.tags]

    def get_tool_names(self) -> List[str]:
        """Get list of tool names."""
        return [tool.name for tool in self.tools]

    def get_ingredient_count(self) -> int:
        """Get number of ingredients."""
        return len(self.recipe_ingredient)

    def get_instruction_count(self) -> int:
        """Get number of instruction steps."""
        return len(self.recipe_instructions)


class RecipeCreateRequest(BaseModel):
    """Request model for creating a new recipe."""

    def __init__(
        self,
        name: str,
        description: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        self.name = name
        self.description = description
        super().__init__(**kwargs)


class RecipeUpdateRequest(BaseModel):
    """Request model for updating an existing recipe."""

    def __init__(
        self,
        name: Optional[str] = None,
        description: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        self.name = name
        self.description = description
        super().__init__(**kwargs)


class RecipeSummary(BaseModel):
    """Lightweight recipe summary for list views."""

    def __init__(
        self,
        id: Optional[str] = None,
        name: str = "",
        slug: str = "",
        image: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        self.id = id
        self.name = name
        self.slug = slug
        self.image = image
        super().__init__(**kwargs)


class RecipeFilter(BaseModel):
    """Filter options for recipe queries."""

    def __init__(
        self,
        page: int = 1,
        per_page: int = 50,
        search: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        self.page = page
        self.per_page = per_page
        self.search = search
        super().__init__(**kwargs)


class RecipeImportRequest(BaseModel):
    """Request model for importing a recipe from URL."""

    def __init__(
        self,
        url: str,
        **kwargs: Any,
    ) -> None:
        self.url = url
        super().__init__(**kwargs)


class BulkRecipeExportRequest(BaseModel):
    """Request model for bulk recipe export."""

    def __init__(
        self,
        recipes: List[str],
        export_type: str = "json",
        **kwargs: Any,
    ) -> None:
        self.recipes = recipes
        self.export_type = export_type
        super().__init__(**kwargs)


class RecipeImageRequest(BaseModel):
    """Request model for recipe image operations."""

    def __init__(
        self,
        extension: str = "webp",
        **kwargs: Any,
    ) -> None:
        self.extension = extension
        super().__init__(**kwargs)

 