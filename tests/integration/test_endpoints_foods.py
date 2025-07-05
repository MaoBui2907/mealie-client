"""
Integration tests for foods endpoint.

Tests cover food CRUD operations, search functionality,
validation scenarios, and food management workflows.
"""

import pytest
import httpx

from mealie_client.exceptions import NotFoundError, ValidationError, AuthorizationError


class TestFoodsCRUD:
    """Test suite for basic food CRUD operations."""

    @pytest.mark.integration
    async def test_get_all_foods(self, integration_httpx_mock, authenticated_client, mock_pagination_response):
        """Test fetching all foods with pagination."""
        foods_response = {
            "items": [
                {
                    "id": "food_1",
                    "name": "Chicken Breast",
                    "description": "Boneless, skinless chicken breast",
                    "created_at": "2023-01-01T00:00:00Z",
                    "updated_at": "2023-01-01T00:00:00Z",
                    "label": {
                        "id": "label_1",
                        "name": "Meat",
                        "color": "#red"
                    },
                    "extras": {
                        "protein_per_100g": "23g",
                        "calories_per_100g": "165"
                    }
                },
                {
                    "id": "food_2",
                    "name": "Broccoli",
                    "description": "Fresh green broccoli",
                    "created_at": "2023-01-02T00:00:00Z",
                    "updated_at": "2023-01-02T00:00:00Z",
                    "label": {
                        "id": "label_2",
                        "name": "Vegetables",
                        "color": "#green"
                    },
                    "extras": {
                        "vitamin_c": "high",
                        "calories_per_100g": "34"
                    }
                }
            ],
            "page": 1,
            "per_page": 50,
            "total": 2
        }
        
        integration_httpx_mock.get("/api/foods").mock(
            return_value=httpx.Response(200, json=foods_response)
        )
        
        foods = await authenticated_client.foods.get_all(page=1, per_page=50)
        
        assert len(foods) == 2
        assert foods[0].name == "Chicken Breast"
        assert foods[0].label["name"] == "Meat"
        assert foods[1].name == "Broccoli"
        assert foods[1].label["name"] == "Vegetables"

    @pytest.mark.integration
    async def test_get_food_by_id(self, integration_httpx_mock, authenticated_client):
        """Test fetching a specific food by ID."""
        food_id = "test-food-123"
        food_data = {
            "id": food_id,
            "name": "Salmon Fillet",
            "description": "Fresh Atlantic salmon fillet",
            "created_at": "2023-01-01T00:00:00Z",
            "updated_at": "2023-01-01T00:00:00Z",
            "label": {
                "id": "seafood_label",
                "name": "Seafood",
                "color": "#blue"
            },
            "extras": {
                "omega_3": "high",
                "protein_per_100g": "25g",
                "calories_per_100g": "208",
                "source": "wild_caught"
            }
        }
        
        integration_httpx_mock.get(f"/api/foods/{food_id}").mock(
            return_value=httpx.Response(200, json=food_data)
        )
        
        food = await authenticated_client.foods.get(food_id)
        
        assert food.id == food_id
        assert food.name == "Salmon Fillet"
        assert food.description == "Fresh Atlantic salmon fillet"
        assert food.label["name"] == "Seafood"

    @pytest.mark.integration
    async def test_get_food_not_found(self, integration_httpx_mock, authenticated_client):
        """Test handling of non-existent food."""
        food_id = "nonexistent-food"
        integration_httpx_mock.get(f"/api/foods/{food_id}").mock(
            return_value=httpx.Response(404, json={"detail": "Food not found"})
        )
        
        with pytest.raises(NotFoundError) as exc_info:
            await authenticated_client.foods.get(food_id)
        
        assert exc_info.value.status_code == 404
        assert exc_info.value.resource_type == "food"
        assert exc_info.value.resource_id == food_id

    @pytest.mark.integration
    async def test_create_food_success(self, integration_httpx_mock, authenticated_client):
        """Test successful food creation."""
        food_data = {
            "name": "Quinoa",
            "description": "Organic quinoa grain",
            "label": {
                "name": "Grains",
                "color": "#brown"
            },
            "extras": {
                "protein_per_100g": "14g",
                "fiber_per_100g": "7g",
                "calories_per_100g": "368"
            }
        }
        
        created_food = {
            "id": "new-food-456",
            **food_data,
            "created_at": "2023-01-01T00:00:00Z",
            "updated_at": "2023-01-01T00:00:00Z"
        }
        
        integration_httpx_mock.post("/api/foods").mock(
            return_value=httpx.Response(201, json=created_food)
        )
        
        food = await authenticated_client.foods.create(food_data)
        
        assert food.id == "new-food-456"
        assert food.name == "Quinoa"
        assert food.description == "Organic quinoa grain"

    @pytest.mark.integration
    async def test_create_food_validation_error(self, integration_httpx_mock, authenticated_client):
        """Test food creation with validation errors."""
        integration_httpx_mock.post("/api/foods").mock(
            return_value=httpx.Response(422, json={
                "detail": [
                    {"loc": ["name"], "msg": "field required", "type": "value_error.missing"},
                    {"loc": ["name"], "msg": "food name already exists", "type": "value_error"}
                ]
            })
        )
        
        with pytest.raises(ValidationError) as exc_info:
            await authenticated_client.foods.create({"description": "Missing name"})
        
        assert exc_info.value.status_code == 422
        assert "field required" in str(exc_info.value)

    @pytest.mark.integration
    async def test_update_food_success(self, integration_httpx_mock, authenticated_client):
        """Test successful food update."""
        food_id = "update-food-789"
        update_data = {
            "description": "Updated organic quinoa description",
            "extras": {
                "protein_per_100g": "15g",  # Updated value
                "fiber_per_100g": "7g",
                "calories_per_100g": "368",
                "organic": True  # New field
            }
        }
        
        updated_food = {
            "id": food_id,
            "name": "Quinoa",
            **update_data,
            "updated_at": "2023-01-01T12:00:00Z"
        }
        
        integration_httpx_mock.put(f"/api/foods/{food_id}").mock(
            return_value=httpx.Response(200, json=updated_food)
        )
        
        food = await authenticated_client.foods.update(food_id, update_data)
        
        assert food.id == food_id
        assert food.description == "Updated organic quinoa description"
        assert food.extras["protein_per_100g"] == "15g"

    @pytest.mark.integration
    async def test_delete_food_success(self, integration_httpx_mock, authenticated_client):
        """Test successful food deletion."""
        food_id = "delete-food-101"
        integration_httpx_mock.delete(f"/api/foods/{food_id}").mock(
            return_value=httpx.Response(204)
        )
        
        result = await authenticated_client.foods.delete(food_id)
        assert result is True

    @pytest.mark.integration
    async def test_delete_food_not_found(self, integration_httpx_mock, authenticated_client):
        """Test deletion of non-existent food."""
        food_id = "nonexistent-food"
        integration_httpx_mock.delete(f"/api/foods/{food_id}").mock(
            return_value=httpx.Response(404, json={"detail": "Food not found"})
        )
        
        with pytest.raises(NotFoundError):
            await authenticated_client.foods.delete(food_id)

class TestFoodsValidation:
    """Test suite for food validation scenarios."""

    @pytest.mark.integration
    async def test_create_food_duplicate_name(self, integration_httpx_mock, authenticated_client):
        """Test creating food with duplicate name."""
        integration_httpx_mock.post("/api/foods").mock(
            return_value=httpx.Response(409, json={
                "detail": "Food with this name already exists"
            })
        )
        
        food_data = {
            "name": "Existing Food",
            "description": "This food already exists"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            await authenticated_client.foods.create(food_data)
        
        assert exc_info.value.status_code == 409

    @pytest.mark.integration
    async def test_create_food_invalid_label(self, integration_httpx_mock, authenticated_client):
        """Test creating food with invalid label."""
        integration_httpx_mock.post("/api/foods").mock(
            return_value=httpx.Response(422, json={
                "detail": [
                    {"loc": ["label"], "msg": "invalid label format", "type": "value_error"}
                ]
            })
        )
        
        food_data = {
            "name": "Test Food",
            "label": "invalid_label_format"  # Should be object
        }
        
        with pytest.raises(ValidationError):
            await authenticated_client.foods.create(food_data)

    @pytest.mark.integration
    async def test_update_food_invalid_extras(self, integration_httpx_mock, authenticated_client):
        """Test updating food with invalid extras format."""
        food_id = "test-food"
        integration_httpx_mock.put(f"/api/foods/{food_id}").mock(
            return_value=httpx.Response(422, json={
                "detail": [
                    {"loc": ["extras"], "msg": "extras must be key-value pairs", "type": "value_error"}
                ]
            })
        )
        
        with pytest.raises(ValidationError):
            await authenticated_client.foods.update(food_id, {"extras": "invalid_format"})


class TestFoodsLabels:
    """Test suite for food label management."""

    @pytest.mark.integration
    async def test_foods_with_different_labels(self, integration_httpx_mock, authenticated_client):
        """Test foods with various label configurations."""
        foods_response = {
            "items": [
                {
                    "id": "food_1",
                    "name": "Beef Steak",
                    "label": {
                        "id": "meat_label",
                        "name": "Meat",
                        "color": "#ff0000"
                    }
                },
                {
                    "id": "food_2",
                    "name": "Carrots",
                    "label": {
                        "id": "veggie_label",
                        "name": "Vegetables",
                        "color": "#00ff00"
                    }
                },
                {
                    "id": "food_3",
                    "name": "Unlabeled Food",
                    "label": None
                }
            ],
            "page": 1,
            "per_page": 50,
            "total": 3
        }
        
        integration_httpx_mock.get("/api/foods").mock(
            return_value=httpx.Response(200, json=foods_response)
        )
        
        foods = await authenticated_client.foods.get_all()
        
        assert len(foods) == 3
        assert foods[0].label["name"] == "Meat"
        assert foods[1].label["name"] == "Vegetables"
        assert foods[2].label is None

    @pytest.mark.integration
    async def test_create_food_with_custom_label(self, integration_httpx_mock, authenticated_client):
        """Test creating food with custom label."""
        food_data = {
            "name": "Exotic Fruit",
            "description": "Rare tropical fruit",
            "label": {
                "name": "Exotic Fruits",
                "color": "#purple"
            }
        }
        
        created_food = {
            "id": "exotic-fruit-id",
            **food_data,
            "created_at": "2023-01-01T00:00:00Z"
        }
        
        integration_httpx_mock.post("/api/foods").mock(
            return_value=httpx.Response(201, json=created_food)
        )
        
        food = await authenticated_client.foods.create(food_data)
        
        assert food.name == "Exotic Fruit"
        assert food.label["name"] == "Exotic Fruits"
        assert food.label["color"] == "#purple"


class TestFoodsWorkflows:
    """Test suite for complex food management workflows."""

    @pytest.mark.integration
    async def test_complete_food_lifecycle(self, integration_httpx_mock, authenticated_client):
        """Test complete food creation, update, and deletion workflow."""
        food_data = {
            "name": "Lifecycle Food",
            "description": "Food for testing lifecycle",
            "label": {
                "name": "Test Foods",
                "color": "#test"
            },
            "extras": {
                "calories": "100",
                "protein": "5g"
            }
        }
        
        # Mock food creation
        created_food = {
            "id": "lifecycle-food-id",
            **food_data,
            "created_at": "2023-01-01T00:00:00Z",
            "updated_at": "2023-01-01T00:00:00Z"
        }
        
        integration_httpx_mock.post("/api/foods").mock(
            return_value=httpx.Response(201, json=created_food)
        )
        
        # Mock food update
        updated_food = {
            **created_food,
            "description": "Updated lifecycle food description",
            "extras": {
                "calories": "110",  # Updated
                "protein": "6g",    # Updated
                "fat": "2g"         # New
            },
            "updated_at": "2023-01-01T12:00:00Z"
        }
        
        integration_httpx_mock.put("/api/foods/lifecycle-food-id").mock(
            return_value=httpx.Response(200, json=updated_food)
        )
        
        # Mock food deletion
        integration_httpx_mock.delete("/api/foods/lifecycle-food-id").mock(
            return_value=httpx.Response(204)
        )
        
        # Execute workflow
        # 1. Create food
        food = await authenticated_client.foods.create(food_data)
        assert food.name == "Lifecycle Food"
        
        # 2. Update food
        updated = await authenticated_client.foods.update(
            food.id,
            {
                "description": "Updated lifecycle food description",
                "extras": {
                    "calories": "110",
                    "protein": "6g",
                    "fat": "2g"
                }
            }
        )
        assert updated.description == "Updated lifecycle food description"
        assert updated.extras["calories"] == "110"
        
        # 3. Delete food
        result = await authenticated_client.foods.delete(food.id)
        assert result is True

    @pytest.mark.integration
    async def test_food_inventory_management_workflow(self, integration_httpx_mock, authenticated_client):
        """Test food inventory management workflow."""
        # Create multiple foods for inventory
        foods_to_create = [
            {
                "name": f"Inventory Food {i}",
                "description": f"Food {i} for inventory management",
                "label": {"name": "Inventory", "color": "#inventory"},
                "extras": {"shelf_life": f"{i * 7} days"}
            }
            for i in range(1, 4)
        ]
        
        created_foods = []
        for i, food_data in enumerate(foods_to_create, 1):
            created_food = {
                "id": f"inventory-food-{i}",
                **food_data,
                "created_at": "2023-01-01T00:00:00Z"
            }
            created_foods.append(created_food)
            
            integration_httpx_mock.post("/api/foods").mock(
                return_value=httpx.Response(201, json=created_food)
            )
        
        # Mock searching inventory foods
        integration_httpx_mock.get("/api/foods").mock(
            return_value=httpx.Response(200, json={
                "items": created_foods,
                "page": 1,
                "per_page": 50,
                "total": 3
            })
        )
        
        # Execute workflow
        # 1. Create inventory foods
        inventory_foods = []
        for food_data in foods_to_create:
            food = await authenticated_client.foods.create(food_data)
            inventory_foods.append(food)
        
        assert len(inventory_foods) == 3
        
    @pytest.mark.integration
    async def test_nutritional_data_management_workflow(self, integration_httpx_mock, authenticated_client):
        """Test managing nutritional data for foods."""
        food_id = "nutritional-food"
        
        # Create food with basic nutritional data
        nutritional_food = {
            "id": food_id,
            "name": "Nutritional Food",
            "description": "Food with detailed nutrition info",
            "extras": {
                "calories_per_100g": "200",
                "protein_per_100g": "10g",
                "carbs_per_100g": "30g",
                "fat_per_100g": "5g"
            }
        }
        
        integration_httpx_mock.post("/api/foods").mock(
            return_value=httpx.Response(201, json=nutritional_food)
        )
        
        # Update with detailed nutritional information
        enhanced_nutritional_data = {
            **nutritional_food,
            "extras": {
                **nutritional_food["extras"],
                "fiber_per_100g": "8g",
                "sugar_per_100g": "5g",
                "sodium_per_100mg": "100mg",
                "vitamin_c_per_100g": "15mg",
                "iron_per_100g": "2mg",
                "calcium_per_100g": "50mg"
            },
            "updated_at": "2023-01-01T12:00:00Z"
        }
        
        integration_httpx_mock.put(f"/api/foods/{food_id}").mock(
            return_value=httpx.Response(200, json=enhanced_nutritional_data)
        )
        
        # Execute workflow
        # 1. Create food with basic nutrition
        food = await authenticated_client.foods.create({
            "name": "Nutritional Food",
            "description": "Food with detailed nutrition info",
            "extras": {
                "calories_per_100g": "200",
                "protein_per_100g": "10g",
                "carbs_per_100g": "30g",
                "fat_per_100g": "5g"
            }
        })
        
        assert food.name == "Nutritional Food"
        assert food.extras["calories_per_100g"] == "200"
        
        # 2. Enhance with detailed nutritional data
        enhanced_food = await authenticated_client.foods.update(
            food.id,
            {
                "extras": {
                    "calories_per_100g": "200",
                    "protein_per_100g": "10g",
                    "carbs_per_100g": "30g",
                    "fat_per_100g": "5g",
                    "fiber_per_100g": "8g",
                    "sugar_per_100g": "5g",
                    "sodium_per_100mg": "100mg",
                    "vitamin_c_per_100g": "15mg",
                    "iron_per_100g": "2mg",
                    "calcium_per_100g": "50mg"
                }
            }
        )
        
        assert enhanced_food.extras["fiber_per_100g"] == "8g"
        assert enhanced_food.extras["vitamin_c_per_100g"] == "15mg" 