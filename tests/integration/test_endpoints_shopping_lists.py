"""
Integration tests for shopping lists endpoint.

Tests cover shopping list CRUD operations, recipe ingredient management,
validation scenarios, and shopping workflows.
"""

import pytest
import httpx
import warnings

from mealie_client.exceptions import NotFoundError, ValidationError, AuthorizationError


class TestShoppingListsCRUD:
    """Test suite for basic shopping list CRUD operations."""

    @pytest.mark.integration
    async def test_get_all_shopping_lists(self, integration_httpx_mock, authenticated_client):
        """Test fetching all shopping lists."""
        lists_response = [
            {
                "id": "list_1",
                "name": "Weekly Groceries",
                "created_at": "2023-12-01T00:00:00Z",
                "updated_at": "2023-12-01T00:00:00Z",
                "group_id": "group_123",
                "user_id": "user_456"
            },
            {
                "id": "list_2",
                "name": "Party Shopping",
                "created_at": "2023-12-02T00:00:00Z",
                "updated_at": "2023-12-02T00:00:00Z",
                "group_id": "group_123",
                "user_id": "user_789"
            }
        ]
        
        integration_httpx_mock.get("/api/households/shopping/lists").mock(
            return_value=httpx.Response(200, json=lists_response)
        )
        
        shopping_lists = await authenticated_client.shopping_lists.get_all()
        
        assert len(shopping_lists) == 2
        assert shopping_lists[0].name == "Weekly Groceries"
        assert shopping_lists[1].name == "Party Shopping"

    @pytest.mark.integration
    async def test_get_all_shopping_lists_paginated(self, integration_httpx_mock, authenticated_client):
        """Test shopping lists endpoint that returns paginated response format."""
        paginated_response = {
            "items": [
                {
                    "id": "list_paged",
                    "name": "Paginated List",
                    "group_id": "group_123"
                }
            ],
            "page": 1,
            "per_page": 50,
            "total": 1
        }
        
        integration_httpx_mock.get("/api/households/shopping/lists").mock(
            return_value=httpx.Response(200, json=paginated_response)
        )
        
        shopping_lists = await authenticated_client.shopping_lists.get_all()
        
        assert len(shopping_lists) == 1
        assert shopping_lists[0].name == "Paginated List"

    @pytest.mark.integration
    async def test_get_shopping_list_by_id(self, integration_httpx_mock, authenticated_client):
        """Test fetching a specific shopping list by ID."""
        list_id = "test-list-123"
        list_data = {
            "id": list_id,
            "name": "Test Shopping List",
            "created_at": "2023-12-01T00:00:00Z",
            "updated_at": "2023-12-01T00:00:00Z",
            "group_id": "group_123",
            "user_id": "user_456",
            "list_items": [
                {
                    "id": "item_1",
                    "checked": False,
                    "position": 1,
                    "is_food": True,
                    "note": "Fresh organic",
                    "quantity": 2.0,
                    "unit": {
                        "id": "unit_1",
                        "name": "cups",
                        "abbreviation": "c"
                    },
                    "food": {
                        "id": "food_1",
                        "name": "Flour",
                        "label": {
                            "id": "label_1",
                            "name": "Pantry",
                            "color": "#blue"
                        }
                    },
                    "recipe_references": [
                        {
                            "id": "ref_1",
                            "recipe_id": "recipe_123",
                            "recipe_quantity": 1.0
                        }
                    ]
                }
            ],
            "recipe_references": [
                {
                    "id": "recipe_123",
                    "name": "Bread Recipe",
                    "quantity": 1.0
                }
            ]
        }
        
        integration_httpx_mock.get(f"/api/households/shopping/lists/{list_id}").mock(
            return_value=httpx.Response(200, json=list_data)
        )
        
        shopping_list = await authenticated_client.shopping_lists.get(list_id)
        
        assert shopping_list.id == list_id
        assert shopping_list.name == "Test Shopping List"
        assert len(shopping_list.list_items) == 1
        assert shopping_list.list_items[0].food["name"] == "Flour"

    @pytest.mark.integration
    async def test_get_shopping_list_not_found(self, integration_httpx_mock, authenticated_client):
        """Test handling of non-existent shopping list."""
        list_id = "nonexistent-list"
        integration_httpx_mock.get(f"/api/households/shopping/lists/{list_id}").mock(
            return_value=httpx.Response(404, json={"detail": "Shopping list not found"})
        )
        
        with pytest.raises(NotFoundError) as exc_info:
            await authenticated_client.shopping_lists.get(list_id)
        
        assert exc_info.value.status_code == 404
        assert exc_info.value.resource_type == "shopping_list"
        assert exc_info.value.resource_id == list_id

    @pytest.mark.integration
    async def test_create_shopping_list_success(self, integration_httpx_mock, authenticated_client):
        """Test successful shopping list creation."""
        list_data = {
            "name": "New Shopping List",
            "extras": {
                "created_by": "integration_test"
            }
        }
        
        created_list = {
            "id": "new-list-456",
            **list_data,
            "created_at": "2023-12-01T00:00:00Z",
            "updated_at": "2023-12-01T00:00:00Z",
            "group_id": "group_123",
            "user_id": "user_456",
            "list_items": []
        }
        
        integration_httpx_mock.post("/api/households/shopping/lists").mock(
            return_value=httpx.Response(201, json=created_list)
        )
        
        shopping_list = await authenticated_client.shopping_lists.create(list_data)
        
        assert shopping_list.id == "new-list-456"
        assert shopping_list.name == "New Shopping List"

    @pytest.mark.integration
    async def test_create_shopping_list_validation_error(self, integration_httpx_mock, authenticated_client):
        """Test shopping list creation with validation errors."""
        integration_httpx_mock.post("/api/households/shopping/lists").mock(
            return_value=httpx.Response(422, json={
                "detail": [
                    {"loc": ["name"], "msg": "field required", "type": "value_error.missing"}
                ]
            })
        )
        
        with pytest.raises(ValidationError) as exc_info:
            await authenticated_client.shopping_lists.create({})
        
        assert exc_info.value.status_code == 422
        assert "field required" in str(exc_info.value)

    @pytest.mark.integration
    async def test_update_shopping_list_success(self, integration_httpx_mock, authenticated_client):
        """Test successful shopping list update."""
        list_id = "update-list-789"
        update_data = {
            "name": "Updated Shopping List",
            "extras": {
                "updated_by": "integration_test"
            }
        }
        
        updated_list = {
            "id": list_id,
            **update_data,
            "created_at": "2023-12-01T00:00:00Z",
            "updated_at": "2023-12-01T12:00:00Z",
            "group_id": "group_123"
        }
        
        integration_httpx_mock.put(f"/api/households/shopping/lists/{list_id}").mock(
            return_value=httpx.Response(200, json=updated_list)
        )
        
        shopping_list = await authenticated_client.shopping_lists.update(list_id, update_data)
        
        assert shopping_list.id == list_id
        assert shopping_list.name == "Updated Shopping List"

    @pytest.mark.integration
    async def test_delete_shopping_list_success(self, integration_httpx_mock, authenticated_client):
        """Test successful shopping list deletion."""
        list_id = "delete-list-101"
        integration_httpx_mock.delete(f"/api/households/shopping/lists/{list_id}").mock(
            return_value=httpx.Response(204)
        )
        
        result = await authenticated_client.shopping_lists.delete(list_id)
        assert result is True

    @pytest.mark.integration
    async def test_delete_shopping_list_not_found(self, integration_httpx_mock, authenticated_client):
        """Test deletion of non-existent shopping list."""
        list_id = "nonexistent-list"
        integration_httpx_mock.delete(f"/api/households/shopping/lists/{list_id}").mock(
            return_value=httpx.Response(404, json={"detail": "Shopping list not found"})
        )
        
        with pytest.raises(NotFoundError):
            await authenticated_client.shopping_lists.delete(list_id)


class TestShoppingListsRecipeIngredients:
    """Test suite for recipe ingredient management in shopping lists."""

    @pytest.mark.integration
    async def test_add_recipe_ingredients_success(self, integration_httpx_mock, authenticated_client):
        """Test successfully adding recipe ingredients to shopping list."""
        list_id = "ingredients-list-123"
        recipe_data = [
            {
                "recipe_id": "recipe_123",
                "recipe_quantity": 2.0,
                "recipe_ingredients": [
                    {
                        "title": "Main Ingredients",
                        "note": "Fresh organic flour",
                        "unit": {"name": "cups"},
                        "food": {"name": "Flour"},
                        "quantity": 2.0
                    },
                    {
                        "title": "Main Ingredients",
                        "note": "Large eggs",
                        "unit": {"name": "pieces"},
                        "food": {"name": "Eggs"},
                        "quantity": 3.0
                    }
                ]
            }
        ]
        
        updated_list = {
            "id": list_id,
            "name": "Updated with Recipe Ingredients",
            "list_items": [
                {
                    "id": "item_1",
                    "food": {"name": "Flour"},
                    "quantity": 4.0,  # 2 * 2.0 recipe quantity
                    "unit": {"name": "cups"},
                    "recipe_references": [{"recipe_id": "recipe_123"}]
                },
                {
                    "id": "item_2",
                    "food": {"name": "Eggs"},
                    "quantity": 6.0,  # 3 * 2.0 recipe quantity
                    "unit": {"name": "pieces"},
                    "recipe_references": [{"recipe_id": "recipe_123"}]
                }
            ]
        }
        
        integration_httpx_mock.post(f"/api/households/shopping/lists/{list_id}/recipe").mock(
            return_value=httpx.Response(200, json=updated_list)
        )
        
        shopping_list = await authenticated_client.shopping_lists.add_recipe_ingredients(
            list_id, recipe_data
        )
        
        assert shopping_list.id == list_id
        assert len(shopping_list.list_items) == 2
        assert shopping_list.list_items[0].food["name"] == "Flour"
        assert shopping_list.list_items[0].quantity == 4.0

    @pytest.mark.integration
    async def test_add_single_recipe_ingredients(self, integration_httpx_mock, authenticated_client):
        """Test adding ingredients from a single recipe."""
        list_id = "single-recipe-list"
        recipe_id = "single_recipe_123"
        
        updated_list = {
            "id": list_id,
            "name": "Single Recipe List",
            "list_items": [
                {
                    "id": "item_1",
                    "food": {"name": "Tomatoes"},
                    "quantity": 3.0,
                    "unit": {"name": "pieces"},
                    "recipe_references": [{"recipe_id": recipe_id}]
                }
            ]
        }
        
        integration_httpx_mock.post(f"/api/households/shopping/lists/{list_id}/recipe/{recipe_id}").mock(
            return_value=httpx.Response(200, json=updated_list)
        )
        
        shopping_list = await authenticated_client.shopping_lists.add_single_recipe_ingredients(
            list_id, recipe_id
        )
        
        assert shopping_list.id == list_id
        assert len(shopping_list.list_items) == 1
        assert shopping_list.list_items[0].food["name"] == "Tomatoes"

    @pytest.mark.integration
    async def test_remove_recipe_ingredients(self, integration_httpx_mock, authenticated_client):
        """Test removing recipe ingredients from shopping list."""
        list_id = "remove-ingredients-list"
        recipe_id = "recipe_to_remove"
        decrement_data = {
            "recipe_id": recipe_id,
            "recipe_quantity": 1.0
        }
        
        updated_list = {
            "id": list_id,
            "name": "After Ingredient Removal",
            "list_items": []  # All ingredients removed
        }
        
        integration_httpx_mock.post(f"/api/households/shopping/lists/{list_id}/recipe/{recipe_id}/delete").mock(
            return_value=httpx.Response(200, json=updated_list)
        )
        
        shopping_list = await authenticated_client.shopping_lists.remove_recipe_ingredients(
            list_id, recipe_id, decrement_data
        )
        
        assert shopping_list.id == list_id
        assert len(shopping_list.list_items) == 0

    @pytest.mark.integration
    async def test_add_recipe_ingredients_invalid_recipe(self, integration_httpx_mock, authenticated_client):
        """Test adding ingredients with invalid recipe data."""
        list_id = "invalid-recipe-list"
        integration_httpx_mock.post(f"/api/households/shopping/lists/{list_id}/recipe").mock(
            return_value=httpx.Response(422, json={
                "detail": [
                    {"loc": ["recipe_id"], "msg": "invalid recipe format", "type": "value_error"}
                ]
            })
        )
        
        invalid_recipe_data = [{"invalid": "data"}]
        
        with pytest.raises(ValidationError):
            await authenticated_client.shopping_lists.add_recipe_ingredients(
                list_id, invalid_recipe_data
            )


class TestShoppingListsDeprecatedMethods:
    """Test suite for deprecated item management methods."""

    @pytest.mark.integration
    async def test_add_item_deprecated_warning(self, integration_httpx_mock, authenticated_client):
        """Test that add_item method shows deprecation warning."""
        list_id = "deprecated-test-list"
        item_data = {
            "food": {"name": "Test Food"},
            "quantity": 1.0,
            "unit": {"name": "pieces"}
        }
        
        # Mock response even though method is deprecated
        integration_httpx_mock.post(f"/api/households/shopping/lists/{list_id}/items").mock(
            return_value=httpx.Response(200, json={"id": list_id, "list_items": []})
        )
        
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            
            await authenticated_client.shopping_lists.add_item(list_id, item_data)
            
            assert len(w) == 1
            assert issubclass(w[0].category, DeprecationWarning)
            assert "add_item() is deprecated" in str(w[0].message)

    @pytest.mark.integration
    async def test_update_item_deprecated_warning(self, integration_httpx_mock, authenticated_client):
        """Test that update_item method shows deprecation warning."""
        list_id = "deprecated-test-list"
        item_id = "deprecated-item"
        item_data = {"quantity": 2.0}
        
        # Mock response even though method is deprecated
        integration_httpx_mock.put(f"/api/households/shopping/lists/{list_id}/items/{item_id}").mock(
            return_value=httpx.Response(200, json={"id": list_id, "list_items": []})
        )
        
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            
            await authenticated_client.shopping_lists.update_item(list_id, item_id, item_data)
            
            assert len(w) == 1
            assert issubclass(w[0].category, DeprecationWarning)
            assert "update_item() is deprecated" in str(w[0].message)

    @pytest.mark.integration
    async def test_delete_item_deprecated_warning(self, integration_httpx_mock, authenticated_client):
        """Test that delete_item method shows deprecation warning."""
        list_id = "deprecated-test-list"
        item_id = "deprecated-item"
        
        # Mock response even though method is deprecated
        integration_httpx_mock.delete(f"/api/households/shopping/lists/{list_id}/items/{item_id}").mock(
            return_value=httpx.Response(204)
        )
        
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            
            await authenticated_client.shopping_lists.delete_item(list_id, item_id)
            
            assert len(w) == 1
            assert issubclass(w[0].category, DeprecationWarning)
            assert "delete_item() is deprecated" in str(w[0].message)


class TestShoppingListsLabelManagement:
    """Test suite for shopping list label settings management."""

    @pytest.mark.integration
    async def test_update_label_settings(self, integration_httpx_mock, authenticated_client):
        """Test updating label settings for shopping list."""
        list_id = "label-settings-list"
        label_settings = [
            {
                "id": "label_1",
                "name": "Produce",
                "color": "#green",
                "position": 1
            },
            {
                "id": "label_2", 
                "name": "Dairy",
                "color": "#blue",
                "position": 2
            }
        ]
        
        updated_list = {
            "id": list_id,
            "name": "List with Label Settings",
            "label_settings": label_settings
        }
        
        integration_httpx_mock.put(f"/api/households/shopping/lists/{list_id}/label-settings").mock(
            return_value=httpx.Response(200, json=updated_list)
        )
        
        shopping_list = await authenticated_client.shopping_lists.update_label_settings(
            list_id, label_settings
        )
        
        assert shopping_list.id == list_id
        assert hasattr(shopping_list, 'label_settings')

    @pytest.mark.integration
    async def test_clear_checked_items(self, integration_httpx_mock, authenticated_client):
        """Test clearing checked items from shopping list."""
        list_id = "clear-checked-list"
        
        updated_list = {
            "id": list_id,
            "name": "List After Clear",
            "list_items": [
                {
                    "id": "unchecked_item",
                    "checked": False,
                    "food": {"name": "Unchecked Item"}
                }
                # All checked items removed
            ]
        }
        
        integration_httpx_mock.delete(f"/api/households/shopping/lists/{list_id}/items/checked").mock(
            return_value=httpx.Response(200, json=updated_list)
        )
        
        shopping_list = await authenticated_client.shopping_lists.clear_checked_items(list_id)
        
        assert shopping_list.id == list_id
        assert len(shopping_list.list_items) == 1
        assert shopping_list.list_items[0].checked is False


class TestShoppingListsWorkflows:
    """Test suite for complex shopping list workflows."""

    @pytest.mark.integration
    async def test_meal_planning_shopping_workflow(self, integration_httpx_mock, authenticated_client):
        """Test complete meal planning to shopping list workflow."""
        # Create shopping list
        list_data = {"name": "Weekly Meal Plan Shopping"}
        created_list = {
            "id": "meal-plan-list",
            **list_data,
            "list_items": []
        }
        
        integration_httpx_mock.post("/api/households/shopping/lists").mock(
            return_value=httpx.Response(201, json=created_list)
        )
        
        # Add multiple recipes to the list
        recipes_data = [
            {
                "recipe_id": "monday_dinner",
                "recipe_quantity": 1.0,
                "recipe_ingredients": [
                    {
                        "food": {"name": "Chicken Breast"},
                        "quantity": 4.0,
                        "unit": {"name": "pieces"}
                    }
                ]
            },
            {
                "recipe_id": "tuesday_lunch",
                "recipe_quantity": 1.0,
                "recipe_ingredients": [
                    {
                        "food": {"name": "Lettuce"},
                        "quantity": 1.0,
                        "unit": {"name": "head"}
                    }
                ]
            }
        ]
        
        updated_with_recipes = {
            "id": "meal-plan-list",
            "name": "Weekly Meal Plan Shopping",
            "list_items": [
                {
                    "id": "item_1",
                    "food": {"name": "Chicken Breast"},
                    "quantity": 4.0,
                    "recipe_references": [{"recipe_id": "monday_dinner"}]
                },
                {
                    "id": "item_2",
                    "food": {"name": "Lettuce"},
                    "quantity": 1.0,
                    "recipe_references": [{"recipe_id": "tuesday_lunch"}]
                }
            ]
        }
        
        integration_httpx_mock.post("/api/households/shopping/lists/meal-plan-list/recipe").mock(
            return_value=httpx.Response(200, json=updated_with_recipes)
        )
        
        # Execute workflow
        # 1. Create shopping list
        shopping_list = await authenticated_client.shopping_lists.create(list_data)
        assert shopping_list.name == "Weekly Meal Plan Shopping"
        
        # 2. Add recipes to shopping list
        updated_list = await authenticated_client.shopping_lists.add_recipe_ingredients(
            shopping_list.id, recipes_data
        )
        
        assert len(updated_list.list_items) == 2
        assert updated_list.list_items[0].food["name"] == "Chicken Breast"
        assert updated_list.list_items[1].food["name"] == "Lettuce"

    @pytest.mark.integration
    async def test_shopping_list_organization_workflow(self, integration_httpx_mock, authenticated_client):
        """Test organizing shopping list with labels and categories."""
        list_id = "organized-list"
        
        # Update label settings
        label_settings = [
            {"id": "produce", "name": "Produce", "color": "#green", "position": 1},
            {"id": "meat", "name": "Meat", "color": "#red", "position": 2},
            {"id": "dairy", "name": "Dairy", "color": "#blue", "position": 3}
        ]
        
        list_with_labels = {
            "id": list_id,
            "name": "Organized Shopping List",
            "label_settings": label_settings
        }
        
        integration_httpx_mock.put(f"/api/households/shopping/lists/{list_id}/label-settings").mock(
            return_value=httpx.Response(200, json=list_with_labels)
        )
        
        # Add categorized items
        organized_items = {
            "id": list_id,
            "name": "Organized Shopping List",
            "label_settings": label_settings,
            "list_items": [
                {
                    "id": "item_1",
                    "food": {"name": "Apples", "label": {"name": "Produce"}},
                    "quantity": 6.0,
                    "position": 1
                },
                {
                    "id": "item_2",
                    "food": {"name": "Ground Beef", "label": {"name": "Meat"}},
                    "quantity": 1.0,
                    "position": 2
                }
            ]
        }
        
        integration_httpx_mock.get(f"/api/households/shopping/lists/{list_id}").mock(
            return_value=httpx.Response(200, json=organized_items)
        )
        
        # Execute workflow
        # 1. Set up label organization
        organized_list = await authenticated_client.shopping_lists.update_label_settings(
            list_id, label_settings
        )
        assert len(organized_list.label_settings) == 3
        
        # 2. Get organized list with categorized items
        final_list = await authenticated_client.shopping_lists.get(list_id)
        assert len(final_list.list_items) == 2

    @pytest.mark.integration
    async def test_shopping_completion_workflow(self, integration_httpx_mock, authenticated_client):
        """Test shopping completion and cleanup workflow."""
        list_id = "completion-list"
        
        # List with checked and unchecked items
        list_before_clear = {
            "id": list_id,
            "name": "Shopping Completion List",
            "list_items": [
                {
                    "id": "checked_item_1",
                    "checked": True,
                    "food": {"name": "Bought Item 1"}
                },
                {
                    "id": "checked_item_2", 
                    "checked": True,
                    "food": {"name": "Bought Item 2"}
                },
                {
                    "id": "unchecked_item",
                    "checked": False,
                    "food": {"name": "Still Need This"}
                }
            ]
        }
        
        integration_httpx_mock.get(f"/api/households/shopping/lists/{list_id}").mock(
            return_value=httpx.Response(200, json=list_before_clear)
        )
        
        # Clear checked items
        list_after_clear = {
            "id": list_id,
            "name": "Shopping Completion List",
            "list_items": [
                {
                    "id": "unchecked_item",
                    "checked": False,
                    "food": {"name": "Still Need This"}
                }
            ]
        }
        
        integration_httpx_mock.delete(f"/api/households/shopping/lists/{list_id}/items/checked").mock(
            return_value=httpx.Response(200, json=list_after_clear)
        )
        
        # Execute workflow
        # 1. Get list with completed items
        current_list = await authenticated_client.shopping_lists.get(list_id)
        assert len(current_list.list_items) == 3
        
        # 2. Clear completed items
        cleaned_list = await authenticated_client.shopping_lists.clear_checked_items(list_id)
        assert len(cleaned_list.list_items) == 1
        assert cleaned_list.list_items[0].food["name"] == "Still Need This"

    @pytest.mark.integration
    async def test_bulk_recipe_management_workflow(self, integration_httpx_mock, authenticated_client):
        """Test managing multiple recipes in shopping list."""
        list_id = "bulk-recipe-list"
        
        # Add multiple recipes
        bulk_recipes = [
            {"recipe_id": "recipe_1", "recipe_quantity": 2.0},
            {"recipe_id": "recipe_2", "recipe_quantity": 1.0}, 
            {"recipe_id": "recipe_3", "recipe_quantity": 3.0}
        ]
        
        list_with_all_recipes = {
            "id": list_id,
            "name": "Bulk Recipe List",
            "list_items": [
                {"id": f"item_{i}", "recipe_references": [{"recipe_id": f"recipe_{i}"}]}
                for i in range(1, 4)
            ]
        }
        
        integration_httpx_mock.post(f"/api/households/shopping/lists/{list_id}/recipe").mock(
            return_value=httpx.Response(200, json=list_with_all_recipes)
        )
        
        # Remove one recipe
        list_after_removal = {
            "id": list_id,
            "name": "Bulk Recipe List",
            "list_items": [
                {"id": "item_1", "recipe_references": [{"recipe_id": "recipe_1"}]},
                {"id": "item_3", "recipe_references": [{"recipe_id": "recipe_3"}]}
            ]
        }
        
        integration_httpx_mock.post(f"/api/households/shopping/lists/{list_id}/recipe/recipe_2/delete").mock(
            return_value=httpx.Response(200, json=list_after_removal)
        )
        
        # Execute workflow
        # 1. Add multiple recipes
        updated_list = await authenticated_client.shopping_lists.add_recipe_ingredients(
            list_id, bulk_recipes
        )
        assert len(updated_list.list_items) == 3
        
        # 2. Remove one recipe
        final_list = await authenticated_client.shopping_lists.remove_recipe_ingredients(
            list_id, "recipe_2", {"recipe_id": "recipe_2", "recipe_quantity": 1.0}
        )
        assert len(final_list.list_items) == 2 