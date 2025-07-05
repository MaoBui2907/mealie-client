"""
Unit tests for ShoppingListsManager endpoint.

Tests cover shopping list operations including CRUD operations.
"""

from unittest.mock import AsyncMock
from uuid import uuid4
from datetime import UTC, datetime

import pytest

from mealie_client.endpoints.shopping_lists import ShoppingListsManager
from mealie_client.models.shopping_list import ShoppingList, ShoppingListCreateRequest, ShoppingListUpdateRequest
from mealie_client.exceptions import NotFoundError


class TestShoppingListsManager:
    """Test suite for ShoppingListsManager class."""

    @pytest.fixture
    def shopping_lists_manager(self, mealie_client):
        return ShoppingListsManager(mealie_client)

    @pytest.mark.unit
    def test_init(self, mealie_client):
        """Test ShoppingListsManager initialization."""
        manager = ShoppingListsManager(mealie_client)
        assert manager.client == mealie_client

    @pytest.mark.unit
    async def test_get_all(self, shopping_lists_manager):
        """Test get_all shopping lists."""
        mock_response = {"items": [create_test_shopping_list_data() for _ in range(2)]}
        shopping_lists_manager.client.get = AsyncMock(return_value=mock_response)
        
        result = await shopping_lists_manager.get_all()
        
        shopping_lists_manager.client.get.assert_called_once_with("households/shopping/lists")
        assert len(result) == 2

    @pytest.mark.unit
    async def test_get_by_id_success(self, shopping_lists_manager):
        """Test successful get by shopping list ID."""
        list_data = create_test_shopping_list_data()
        shopping_lists_manager.client.get = AsyncMock(return_value=list_data)
        
        result = await shopping_lists_manager.get("list-123")
        
        shopping_lists_manager.client.get.assert_called_once_with("households/shopping/lists/list-123")
        assert isinstance(result, ShoppingList)

    @pytest.mark.unit
    async def test_get_not_found_raises_error(self, shopping_lists_manager):
        """Test that get raises NotFoundError for 404 responses."""
        mock_exception = Exception("Not found")
        mock_exception.status_code = 404
        shopping_lists_manager.client.get = AsyncMock(side_effect=mock_exception)
        
        with pytest.raises(NotFoundError) as exc_info:
            await shopping_lists_manager.get("nonexistent")
        
        assert exc_info.value.resource_type == "shopping_list"
        assert exc_info.value.resource_id == "nonexistent"

    @pytest.mark.unit
    async def test_create(self, shopping_lists_manager):
        """Test shopping list creation."""
        request_data = {
            "name": "Weekly Shopping",
            "group_id": "group-123"
        }
        response_data = create_test_shopping_list_data(name="Weekly Shopping")
        shopping_lists_manager.client.post = AsyncMock(return_value=response_data)
        
        result = await shopping_lists_manager.create(request_data)
        
        shopping_lists_manager.client.post.assert_called_once_with("households/shopping/lists", json_data=request_data)
        assert isinstance(result, ShoppingList)

    @pytest.mark.unit
    async def test_update(self, shopping_lists_manager):
        """Test shopping list update."""
        update_data = {"name": "Updated Shopping List"}
        response_data = create_test_shopping_list_data(name="Updated Shopping List")
        shopping_lists_manager.client.put = AsyncMock(return_value=response_data)
        
        result = await shopping_lists_manager.update("list-123", update_data)
        
        shopping_lists_manager.client.put.assert_called_once_with("households/shopping/lists/list-123", json_data=update_data)
        assert isinstance(result, ShoppingList)

    @pytest.mark.unit
    async def test_delete(self, shopping_lists_manager):
        """Test shopping list deletion."""
        shopping_lists_manager.client.delete = AsyncMock(return_value=None)
        
        result = await shopping_lists_manager.delete("list-123")
        
        shopping_lists_manager.client.delete.assert_called_once_with("households/shopping/lists/list-123")
        assert result is True

    @pytest.mark.unit
    async def test_add_item(self, shopping_lists_manager):
        """Test adding item to shopping list."""
        item_data = {
            "note": "Organic apples",
            "quantity": 6,
            "unit": "pieces"
        }
        response_data = create_test_shopping_list_data()
        shopping_lists_manager.client.post = AsyncMock(return_value=response_data)
        
        result = await shopping_lists_manager.add_item("list-123", item_data)
        
        shopping_lists_manager.client.post.assert_called_once_with("households/shopping/lists/list-123/items", json_data=item_data)
        assert isinstance(result, ShoppingList)

    @pytest.mark.unit
    async def test_update_item(self, shopping_lists_manager):
        """Test updating shopping list item."""
        item_update = {"checked": True, "quantity": 8}
        response_data = create_test_shopping_list_data()
        shopping_lists_manager.client.put = AsyncMock(return_value=response_data)
        
        result = await shopping_lists_manager.update_item("list-123", "item-456", item_update)
        
        shopping_lists_manager.client.put.assert_called_once_with("households/shopping/lists/list-123/items/item-456", json_data=item_update)
        assert isinstance(result, ShoppingList)

    @pytest.mark.unit
    async def test_delete_item(self, shopping_lists_manager):
        """Test deleting shopping list item."""
        shopping_lists_manager.client.delete = AsyncMock(return_value=None)
        
        result = await shopping_lists_manager.delete_item("list-123", "item-456")
        
        shopping_lists_manager.client.delete.assert_called_once_with("households/shopping/lists/list-123/items/item-456")
        assert result is True

def create_test_shopping_list_data(**kwargs):
    """Create test shopping list data."""
    defaults = {
        "id": str(uuid4()),
        "group_id": "test-group",
        "user_id": "test-user",
        "name": f"Test Shopping List {uuid4().hex[:8]}",
        "created_at": datetime.now(UTC).isoformat(),
        "updated_at": datetime.now(UTC).isoformat(),
        "list_items": [
            {
                "id": str(uuid4()),
                "note": "Test item",
                "quantity": 1,
                "unit": "piece",
                "checked": False
            }
        ]
    }
    defaults.update(kwargs)
    return defaults 