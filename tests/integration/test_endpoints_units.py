"""
Integration tests for units endpoint.

Tests cover unit CRUD operations, validation scenarios,
and unit management workflows.
"""

import pytest
import httpx

from mealie_client.exceptions import NotFoundError, ValidationError, AuthorizationError


class TestUnitsCRUD:
    """Test suite for basic unit CRUD operations."""

    @pytest.mark.integration
    async def test_get_all_units(self, integration_httpx_mock, authenticated_client, mock_pagination_response):
        """Test fetching all units with pagination."""
        units_response = {
            "items": [
                {
                    "id": "unit_1",
                    "name": "cups",
                    "description": "Standard measuring cups",
                    "abbreviation": "c",
                    "created_at": "2023-01-01T00:00:00Z",
                    "updated_at": "2023-01-01T00:00:00Z",
                    "fraction": True,
                    "use_abbreviation": True,
                    "extras": {
                        "metric_equivalent": "240ml",
                        "type": "volume"
                    }
                },
                {
                    "id": "unit_2",
                    "name": "grams",
                    "description": "Metric unit of mass",
                    "abbreviation": "g",
                    "created_at": "2023-01-02T00:00:00Z",
                    "updated_at": "2023-01-02T00:00:00Z",
                    "fraction": False,
                    "use_abbreviation": True,
                    "extras": {
                        "base_unit": "kilogram",
                        "type": "weight"
                    }
                }
            ],
            "page": 1,
            "per_page": 50,
            "total": 2
        }
        
        integration_httpx_mock.get("/api/units").mock(
            return_value=httpx.Response(200, json=units_response)
        )
        
        units = await authenticated_client.units.get_all(page=1, per_page=50)
        
        assert len(units) == 2
        assert units[0].name == "cups"
        assert units[0].abbreviation == "c"
        assert units[0].fraction is True
        assert units[1].name == "grams"
        assert units[1].abbreviation == "g"
        assert units[1].fraction is False

    @pytest.mark.integration
    async def test_get_unit_by_id(self, integration_httpx_mock, authenticated_client):
        """Test fetching a specific unit by ID."""
        unit_id = "test-unit-123"
        unit_data = {
            "id": unit_id,
            "name": "tablespoons",
            "description": "Standard tablespoon measurement",
            "abbreviation": "tbsp",
            "created_at": "2023-01-01T00:00:00Z",
            "updated_at": "2023-01-01T00:00:00Z",
            "fraction": True,
            "use_abbreviation": True,
            "extras": {
                "metric_equivalent": "15ml",
                "type": "volume",
                "conversion_to_teaspoons": "3"
            }
        }
        
        integration_httpx_mock.get(f"/api/units/{unit_id}").mock(
            return_value=httpx.Response(200, json=unit_data)
        )
        
        unit = await authenticated_client.units.get(unit_id)
        
        assert unit.id == unit_id
        assert unit.name == "tablespoons"
        assert unit.abbreviation == "tbsp"
        assert unit.description == "Standard tablespoon measurement"
        assert unit.fraction is True

    @pytest.mark.integration
    async def test_get_unit_not_found(self, integration_httpx_mock, authenticated_client):
        """Test handling of non-existent unit."""
        unit_id = "nonexistent-unit"
        integration_httpx_mock.get(f"/api/units/{unit_id}").mock(
            return_value=httpx.Response(404, json={"detail": "Unit not found"})
        )
        
        with pytest.raises(NotFoundError) as exc_info:
            await authenticated_client.units.get(unit_id)
        
        assert exc_info.value.status_code == 404
        assert exc_info.value.resource_type == "unit"
        assert exc_info.value.resource_id == unit_id

    @pytest.mark.integration
    async def test_create_unit_success(self, integration_httpx_mock, authenticated_client):
        """Test successful unit creation."""
        unit_data = {
            "name": "liters",
            "description": "Metric unit of volume",
            "abbreviation": "L",
            "fraction": False,
            "use_abbreviation": True,
            "extras": {
                "base_unit": True,
                "type": "volume",
                "metric": True
            }
        }
        
        created_unit = {
            "id": "new-unit-456",
            **unit_data,
            "created_at": "2023-01-01T00:00:00Z",
            "updated_at": "2023-01-01T00:00:00Z"
        }
        
        integration_httpx_mock.post("/api/units").mock(
            return_value=httpx.Response(201, json=created_unit)
        )
        
        unit = await authenticated_client.units.create(unit_data)
        
        assert unit.id == "new-unit-456"
        assert unit.name == "liters"
        assert unit.abbreviation == "L"
        assert unit.fraction is False

    @pytest.mark.integration
    async def test_create_unit_validation_error(self, integration_httpx_mock, authenticated_client):
        """Test unit creation with validation errors."""
        integration_httpx_mock.post("/api/units").mock(
            return_value=httpx.Response(422, json={
                "detail": [
                    {"loc": ["name"], "msg": "field required", "type": "value_error.missing"},
                    {"loc": ["abbreviation"], "msg": "abbreviation already exists", "type": "value_error"}
                ]
            })
        )
        
        with pytest.raises(ValidationError) as exc_info:
            await authenticated_client.units.create({"description": "Missing name and abbreviation"})
        
        assert exc_info.value.status_code == 422
        assert "field required" in str(exc_info.value)

    @pytest.mark.integration
    async def test_update_unit_success(self, integration_httpx_mock, authenticated_client):
        """Test successful unit update."""
        unit_id = "update-unit-789"
        update_data = {
            "description": "Updated metric unit of volume",
            "extras": {
                "base_unit": True,
                "type": "volume",
                "metric": True,
                "updated": True  # New field
            }
        }
        
        updated_unit = {
            "id": unit_id,
            "name": "liters",
            "abbreviation": "L",
            **update_data,
            "updated_at": "2023-01-01T12:00:00Z"
        }
        
        integration_httpx_mock.put(f"/api/units/{unit_id}").mock(
            return_value=httpx.Response(200, json=updated_unit)
        )
        
        unit = await authenticated_client.units.update(unit_id, update_data)
        
        assert unit.id == unit_id
        assert unit.description == "Updated metric unit of volume"
        assert unit.extras["updated"] is True

    @pytest.mark.integration
    async def test_delete_unit_success(self, integration_httpx_mock, authenticated_client):
        """Test successful unit deletion."""
        unit_id = "delete-unit-101"
        integration_httpx_mock.delete(f"/api/units/{unit_id}").mock(
            return_value=httpx.Response(204)
        )
        
        result = await authenticated_client.units.delete(unit_id)
        assert result is True

    @pytest.mark.integration
    async def test_delete_unit_not_found(self, integration_httpx_mock, authenticated_client):
        """Test deletion of non-existent unit."""
        unit_id = "nonexistent-unit"
        integration_httpx_mock.delete(f"/api/units/{unit_id}").mock(
            return_value=httpx.Response(404, json={"detail": "Unit not found"})
        )
        
        with pytest.raises(NotFoundError):
            await authenticated_client.units.delete(unit_id)


class TestUnitsValidation:
    """Test suite for unit validation scenarios."""

    @pytest.mark.integration
    async def test_create_unit_duplicate_name(self, integration_httpx_mock, authenticated_client):
        """Test creating unit with duplicate name."""
        integration_httpx_mock.post("/api/units").mock(
            return_value=httpx.Response(409, json={
                "detail": "Unit with this name already exists"
            })
        )
        
        unit_data = {
            "name": "existing_unit",
            "abbreviation": "eu",
            "description": "This unit already exists"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            await authenticated_client.units.create(unit_data)
        
        assert exc_info.value.status_code == 409

    @pytest.mark.integration
    async def test_create_unit_duplicate_abbreviation(self, integration_httpx_mock, authenticated_client):
        """Test creating unit with duplicate abbreviation."""
        integration_httpx_mock.post("/api/units").mock(
            return_value=httpx.Response(409, json={
                "detail": "Unit with this abbreviation already exists"
            })
        )
        
        unit_data = {
            "name": "new_unit",
            "abbreviation": "g",  # Already exists
            "description": "New unit with existing abbreviation"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            await authenticated_client.units.create(unit_data)
        
        assert exc_info.value.status_code == 409

    @pytest.mark.integration
    async def test_update_unit_invalid_data(self, integration_httpx_mock, authenticated_client):
        """Test updating unit with invalid data."""
        unit_id = "test-unit"
        integration_httpx_mock.put(f"/api/units/{unit_id}").mock(
            return_value=httpx.Response(422, json={
                "detail": [
                    {"loc": ["fraction"], "msg": "must be boolean", "type": "value_error"}
                ]
            })
        )
        
        with pytest.raises(ValidationError):
            await authenticated_client.units.update(unit_id, {"fraction": "not_boolean"})


class TestUnitsWorkflows:
    """Test suite for complex unit management workflows."""

    @pytest.mark.integration
    async def test_complete_unit_lifecycle(self, integration_httpx_mock, authenticated_client):
        """Test complete unit creation, update, and deletion workflow."""
        unit_data = {
            "name": "lifecycle_unit",
            "description": "Unit for testing lifecycle",
            "abbreviation": "lu",
            "fraction": False,
            "use_abbreviation": True,
            "extras": {
                "type": "test",
                "conversion_factor": "1.0"
            }
        }
        
        # Mock unit creation
        created_unit = {
            "id": "lifecycle-unit-id",
            **unit_data,
            "created_at": "2023-01-01T00:00:00Z",
            "updated_at": "2023-01-01T00:00:00Z"
        }
        
        integration_httpx_mock.post("/api/units").mock(
            return_value=httpx.Response(201, json=created_unit)
        )
        
        # Mock unit update
        updated_unit = {
            **created_unit,
            "description": "Updated lifecycle unit description",
            "fraction": True,  # Changed
            "extras": {
                "type": "test",
                "conversion_factor": "2.0",  # Updated
                "updated": True  # New
            },
            "updated_at": "2023-01-01T12:00:00Z"
        }
        
        integration_httpx_mock.put("/api/units/lifecycle-unit-id").mock(
            return_value=httpx.Response(200, json=updated_unit)
        )
        
        # Mock unit deletion
        integration_httpx_mock.delete("/api/units/lifecycle-unit-id").mock(
            return_value=httpx.Response(204)
        )
        
        # Execute workflow
        # 1. Create unit
        unit = await authenticated_client.units.create(unit_data)
        assert unit.name == "lifecycle_unit"
        
        # 2. Update unit
        updated = await authenticated_client.units.update(
            unit.id,
            {
                "description": "Updated lifecycle unit description",
                "fraction": True,
                "extras": {
                    "type": "test",
                    "conversion_factor": "2.0",
                    "updated": True
                }
            }
        )
        assert updated.description == "Updated lifecycle unit description"
        assert updated.fraction is True
        
        # 3. Delete unit
        result = await authenticated_client.units.delete(unit.id)
        assert result is True

    @pytest.mark.integration
    async def test_unit_measurement_system_workflow(self, integration_httpx_mock, authenticated_client):
        """Test creating measurement systems with related units."""
        # Create metric units
        metric_units = [
            {
                "name": "milliliters",
                "abbreviation": "ml",
                "description": "Metric volume unit",
                "extras": {"system": "metric", "type": "volume", "base_unit": True}
            },
            {
                "name": "grams",
                "abbreviation": "g",
                "description": "Metric weight unit", 
                "extras": {"system": "metric", "type": "weight", "base_unit": True}
            }
        ]
        
        created_metric_units = []
        for i, unit_data in enumerate(metric_units):
            created_unit = {
                "id": f"metric-unit-{i + 1}",
                **unit_data,
                "created_at": "2023-01-01T00:00:00Z"
            }
            created_metric_units.append(created_unit)
            
            integration_httpx_mock.post("/api/units").mock(
                return_value=httpx.Response(201, json=created_unit)
            )
        
        # Mock searching metric units
        integration_httpx_mock.get("/api/units").mock(
            return_value=httpx.Response(200, json={
                "items": created_metric_units,
                "page": 1,
                "per_page": 50,
                "total": 2
            })
        )
        
        # Execute workflow
        # 1. Create metric units
        metric_system_units = []
        for unit_data in metric_units:
            unit = await authenticated_client.units.create(unit_data)
            metric_system_units.append(unit)
        
        assert len(metric_system_units) == 2
        
        # 2. Search metric units
        search_results = await authenticated_client.units.get_all()
        assert len(search_results) == 2
        assert all(unit.extras.get("system") == "metric" for unit in search_results)
