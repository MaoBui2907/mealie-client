"""E2E Test Data Factory

Provides utilities for generating test data for E2E tests.
"""

import time
import uuid
from datetime import datetime, date, timedelta
from typing import Dict, Any, List, Optional

from tests.e2e.config import get_test_config


class E2EDataFactory:
    """Factory for generating E2E test data."""

    @staticmethod
    def generate_unique_id(prefix: str = "") -> str:
        """Generate a unique ID with optional prefix."""
        return f"{prefix}{uuid.uuid4().hex[:8]}"

    def generate_test_recipe_data(
        self, include_advanced_fields: bool = False, name_suffix: str = None
    ) -> Dict[str, Any]:
        """
        Generate test recipe data.

        Args:
            include_advanced_fields: Whether to include advanced fields like ingredients/instructions
            name_suffix: Optional suffix to add to the recipe name for uniqueness

        Returns:
            Dictionary containing recipe data
        """
        # Generate unique identifier to avoid naming conflicts
        unique_id = f"{int(time.time() * 1000)}"  # More precise timestamp
        if name_suffix:
            unique_id += f"-{name_suffix}"

        timestamp = datetime.now().isoformat()

        recipe_data = {
            "name": f"E2E Recipe {unique_id}",
            "description": f"E2E test recipe created at {timestamp}",
            "recipe_yield": 4,
            "prep_time": "PT15M",  # 15 minutes in ISO 8601 duration format
            "cook_time": "PT30M",  # 30 minutes in ISO 8601 duration format
            "total_time": "PT45M",  # 45 minutes total
        }

        if include_advanced_fields:
            recipe_data.update(
                {
                    "recipe_ingredient": [
                        {"title": "Test Ingredient 1", "note": "2 cups"},
                        {"title": "Test Ingredient 2", "note": "1 tablespoon"},
                    ],
                    "recipe_instructions": [
                        {"title": "Step 1", "text": "First test instruction"},
                        {"title": "Step 2", "text": "Second test instruction"},
                    ],
                    "tags": [{"name": f"e2e-tag-{unique_id}"}],
                    "recipe_category": [{"name": f"E2E Category {unique_id}"}],
                    "nutrition": {
                        "calories": "250",
                        "protein": "15g",
                        "carbohydrates": "30g",
                    },
                }
            )

        return recipe_data

    @staticmethod
    def generate_test_user_data(
        username_suffix: Optional[str] = None, **overrides: Any
    ) -> Dict[str, Any]:
        """Generate realistic user data for testing."""
        config = get_test_config()
        suffix = username_suffix or E2EDataFactory.generate_unique_id()

        base_data = {
            "username": f"{config.test_user_prefix}{suffix}",
            "email": f"{config.test_user_prefix}{suffix}@e2etest.local",
            "full_name": f"E2E Test User {suffix}",
            "password": "E2ETestPassword123!",
            "admin": False,
        }

        base_data.update(overrides)
        return base_data

    @staticmethod
    def generate_test_group_data(
        name_suffix: Optional[str] = None, **overrides: Any
    ) -> Dict[str, Any]:
        """Generate realistic group data for testing."""
        config = get_test_config()
        suffix = name_suffix or E2EDataFactory.generate_unique_id()

        base_data = {
            "name": f"{config.test_group_prefix}{suffix}",
            "slug": f"{config.test_group_prefix}{suffix}",
            "preferences": {
                "private_group": False,
                "first_day_of_week": 0,
                "recipe_public": True,
                "recipe_show_nutrition": True,
                "recipe_show_assets": True,
                "recipe_landscape_view": True,
                "recipe_disable_comments": False,
                "recipe_disable_amount": False,
            },
        }

        base_data.update(overrides)
        return base_data

    @staticmethod
    def generate_test_meal_plan_data(
        plan_date: Optional[date] = None, **overrides: Any
    ) -> Dict[str, Any]:
        """Generate realistic meal plan data for testing."""
        config = get_test_config()
        plan_date = plan_date or date.today() + timedelta(days=1)

        base_data = {
            "date": plan_date.isoformat(),
            "entry_type": "breakfast",
            "title": f"{config.test_prefix}meal_plan_{E2EDataFactory.generate_unique_id()}",
            "text": f"E2E test meal plan created at {datetime.utcnow().isoformat()}",
        }

        base_data.update(overrides)
        return base_data

    @staticmethod
    def generate_test_label_data(
        name_suffix: Optional[str] = None, **overrides: Any
    ) -> Dict[str, Any]:
        """Generate realistic label data for testing."""
        config = get_test_config()
        suffix = name_suffix or E2EDataFactory.generate_unique_id()

        base_data = {
            "name": f"{config.test_prefix}label_{suffix}",
            "color": "#000000",
        }

        base_data.update(overrides)
        return base_data

    @staticmethod
    def generate_test_shopping_list_data(
        name_suffix: Optional[str] = None, include_items: bool = True, **overrides: Any
    ) -> Dict[str, Any]:
        """Generate realistic shopping list data for testing."""
        config = get_test_config()
        suffix = name_suffix or E2EDataFactory.generate_unique_id()

        base_data = {
            "name": f"{config.test_prefix}shopping_list_{suffix}",
            "extras": {
                "created_by_test": True,
                "test_timestamp": datetime.utcnow().isoformat(),
            },
        }

        if include_items:
            base_data["list_items"] = [
                {
                    "note": f"E2E test item 1 - {suffix}",
                    "quantity": 2.0,
                    "unit": {"name": "cups"},
                    "food": {"name": "flour"},
                    "checked": False,
                },
                {
                    "note": f"E2E test item 2 - {suffix}",
                    "quantity": 1.0,
                    "unit": {"name": "teaspoon"},
                    "food": {"name": "salt"},
                    "checked": False,
                },
            ]

        base_data.update(overrides)
        return base_data

    @staticmethod
    def generate_test_shopping_list_item_data(
        note_suffix: Optional[str] = None, **overrides: Any
    ) -> Dict[str, Any]:
        """Generate realistic shopping list item data for testing."""
        config = get_test_config()
        suffix = note_suffix or E2EDataFactory.generate_unique_id()

        base_data = {
            "note": f"{config.test_prefix}item_{suffix}",
            "quantity": 1.0,
            "unit": {"name": "piece"},
            "food": {"name": "test food"},
            "checked": False,
            "extras": {
                "created_by_test": True,
                "test_timestamp": datetime.utcnow().isoformat(),
            },
        }

        base_data.update(overrides)
        return base_data

    @staticmethod
    def generate_test_food_data(
        name_suffix: Optional[str] = None, **overrides: Any
    ) -> Dict[str, Any]:
        """Generate realistic food data for testing."""
        config = get_test_config()
        suffix = name_suffix or E2EDataFactory.generate_unique_id()

        # Add timestamp to ensure uniqueness
        timestamp_id = f"{int(time.time() * 1000)}"
        unique_suffix = f"{suffix}_{timestamp_id}"

        base_data = {
            "name": f"{config.test_prefix}food_{unique_suffix}",
            "pluralName": f"{config.test_prefix}foods_{unique_suffix}",
            "description": f"E2E test food created at {datetime.utcnow().isoformat()}",
            "extras": {
                "created_by_test": True,
                "test_timestamp": datetime.utcnow().isoformat(),
            },
            "aliases": [
                {"name": f"test_alias_{unique_suffix}"}
            ],  # Changed: objects instead of strings
        }

        base_data.update(overrides)
        return base_data

    @staticmethod
    def generate_test_unit_data(
        name_suffix: Optional[str] = None, **overrides: Any
    ) -> Dict[str, Any]:
        """Generate realistic unit data for testing."""
        config = get_test_config()
        suffix = name_suffix or E2EDataFactory.generate_unique_id()

        # Add timestamp to ensure uniqueness
        timestamp_id = f"{int(time.time() * 1000)}"
        unique_suffix = f"{suffix}_{timestamp_id}"

        base_data = {
            "name": f"{config.test_prefix}unit_{unique_suffix}",
            "pluralName": f"{config.test_prefix}units_{unique_suffix}",
            "description": f"E2E test unit created at {datetime.utcnow().isoformat()}",
            "abbreviation": f"tu{unique_suffix[:3]}",
            "pluralAbbreviation": f"tus{unique_suffix[:3]}",
            "fraction": False,
            "useAbbreviation": False,
            "extras": {
                "created_by_test": True,
                "test_timestamp": datetime.utcnow().isoformat(),
            },
            "aliases": [
                {"name": f"test_unit_alias_{unique_suffix}"}
            ],  # Changed: objects instead of strings
        }

        base_data.update(overrides)
        return base_data

    @staticmethod
    def generate_test_household_data(
        name_suffix: Optional[str] = None, **overrides: Any
    ) -> Dict[str, Any]:
        """Generate realistic household data for testing."""
        config = get_test_config()
        suffix = name_suffix or E2EDataFactory.generate_unique_id()

        base_data = {
            "name": f"{config.test_prefix}household_{suffix}",
            "slug": f"{config.test_prefix}household_{suffix}",
            "preferences": {
                "privateHousehold": False,
                "lockRecipeEditsFromOtherHouseholds": False,
                "firstDayOfWeek": 0,
                "recipePublic": True,
                "recipeShowNutrition": True,
                "recipeShowAssets": True,
                "recipeLandscapeView": False,
                "recipeDisableComments": False,
                "recipeDisableAmount": True,
            },
        }

        base_data.update(overrides)
        return base_data


# Convenience functions
def generate_test_recipe_data(**kwargs) -> Dict[str, Any]:
    """Generate test recipe data."""
    return E2EDataFactory.generate_test_recipe_data(**kwargs)


def generate_test_user_data(**kwargs) -> Dict[str, Any]:
    """Generate test user data."""
    return E2EDataFactory.generate_test_user_data(**kwargs)


def generate_test_group_data(**kwargs) -> Dict[str, Any]:
    """Generate test group data."""
    return E2EDataFactory.generate_test_group_data(**kwargs)


def generate_test_meal_plan_data(**kwargs) -> Dict[str, Any]:
    """Generate test meal plan data."""
    return E2EDataFactory.generate_test_meal_plan_data(**kwargs)


def generate_test_shopping_list_data(**kwargs) -> Dict[str, Any]:
    """Convenience function for generating test shopping list data."""
    return E2EDataFactory.generate_test_shopping_list_data(**kwargs)


def generate_test_food_data(**kwargs) -> Dict[str, Any]:
    """Convenience function for generating test food data."""
    return E2EDataFactory.generate_test_food_data(**kwargs)


def generate_test_unit_data(**kwargs) -> Dict[str, Any]:
    """Convenience function for generating test unit data."""
    return E2EDataFactory.generate_test_unit_data(**kwargs)


def generate_test_household_data(**kwargs) -> Dict[str, Any]:
    """Convenience function for generating test household data."""
    return E2EDataFactory.generate_test_household_data(**kwargs)
