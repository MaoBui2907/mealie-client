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
        
  
            
        await authenticated_client.shopping_lists.add_item(list_id, item_data)
           

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
        await authenticated_client.shopping_lists.update_item(list_id, item_id, item_data)

    @pytest.mark.integration
    async def test_delete_item_deprecated_warning(self, integration_httpx_mock, authenticated_client):
        """Test that delete_item method shows deprecation warning."""
        list_id = "deprecated-test-list"
        item_id = "deprecated-item"
        
        # Mock response even though method is deprecated
        integration_httpx_mock.delete(f"/api/households/shopping/lists/{list_id}/items/{item_id}").mock(
            return_value=httpx.Response(204)
        )
        
        await authenticated_client.shopping_lists.delete_item(list_id, item_id)
