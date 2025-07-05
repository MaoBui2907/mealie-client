"""
Units endpoint manager for the Mealie SDK.

This module provides comprehensive unit management functionality including
CRUD operations, searching, filtering, and unit-specific features.

"""

from typing import Any, List, Optional

from ..models.common import OrderDirection, OrderByNullPosition
from ..models.unit import Unit, UnitCreateRequest, UnitSummary, UnitUpdateRequest, UnitFilter
from ..exceptions import NotFoundError


class UnitsManager:
    """Manages unit-related API operations.
    
    This module provides comprehensive unit management functionality including
    CRUD operations, searching, filtering, and unit-specific features.

    """

    def __init__(self, client: Any) -> None:
        self.client = client

    async def get_all(
        self,
        page: int = 1,
        per_page: int = 50,
        order_by: Optional[str] = None,
        order_direction: OrderDirection = OrderDirection.ASC,
        order_by_null_position: OrderByNullPosition = OrderByNullPosition.LAST,
        search: Optional[str] = None,
        accept_language: Optional[str] = None,
    ) -> List[UnitSummary]:
        """
        Get all units with optional filtering and pagination.
        
        Args:
            page: Page number (1-based)
            per_page: Number of units per page (API may ignore -1 for all)
            order_by: Field to order by (name, abbreviation, createdAt, etc.)
            order_direction: Order direction (asc or desc)
            order_by_null_position: Position of null values in ordering (first or last)
            search: Search term for unit names/description/abbreviation
        
        Returns:
            List of unit summaries
        
        Raises:
            MealieAPIError: If the API request fails
        """
        unit_filter = UnitFilter(
            page=page,
            per_page=per_page,
            order_by=order_by,
            order_direction=order_direction,
            order_by_null_position=order_by_null_position,
            search=search,
            accept_language=accept_language,
        )

        response = await self.client.get("units", params=unit_filter.to_params())

        if isinstance(response, list):
            units_data = response
            metadata = {
                "page": page,
                "per_page": per_page,
                "total": len(response),
                "total_pages": page,
            }
        elif isinstance(response, dict) and "items" in response:
            units_data = response["items"]
            metadata = {
                "page": response.get("page", page),
                "per_page": response.get("perPage", per_page),
                "total": response.get("total", 0),
                "total_pages": response.get("totalPages", 0),
            }
        else:
            units_data = []
            metadata = {
                "page": page,
                "per_page": per_page,
                "total": 0,
                "total_pages": 0,
            }
        
        return [
            UnitSummary.from_dict(unit_data) if isinstance(unit_data, dict) else unit_data
            for unit_data in units_data
        ]

    async def get(self, unit_id: str) -> Unit:
        """
        Get a specific unit by ID.
        
        Args:
            unit_id: Unit ID identifier
            
        Returns:
            Complete unit object
            
        Raises:
            NotFoundError: If unit not found
            MealieAPIError: If the API request fails
        """
        try:
            response = await self.client.get(f"units/{unit_id}")
            
            # Mealie API returns HTML content instead of JSON 404 for non-existent units
            # This is a quirk of how Mealie handles routing - it falls back to the web interface
            if isinstance(response, bytes):
                # Check if it's HTML content (indicates unit not found)
                response_text = response.decode('utf-8', errors='ignore').lower()
                if '<!doctype html>' in response_text or '<html' in response_text:
                    raise NotFoundError(
                        f"Unit '{unit_id}' not found",
                        resource_type="unit",
                        resource_id=unit_id,
                    )
            if not isinstance(response, dict):
                raise ValueError("Response must be a dictionary")
            return Unit.from_dict(response)
        except Exception as e:
            # Handle traditional 404 errors if they occur
            if hasattr(e, 'status_code') and getattr(e, 'status_code') == 404:
                raise NotFoundError(
                    f"Unit '{unit_id}' not found",
                    resource_type="unit",
                    resource_id=unit_id,
                )
            raise 
        
    async def create(self, unit: UnitCreateRequest) -> Unit:
        """
        Create a new unit.
        
        Args:
            unit: Unit object or dict to create
            
        Returns:
            Created unit object 
            
        Raises:
            MealieAPIError: If the API request fails
        """
        if hasattr(unit, 'to_dict'):
            unit_data = unit.to_dict()
        else:
            unit_data = unit
        response = await self.client.post("units", json_data=unit_data)
        return Unit.from_dict(response) if isinstance(response, dict) else response
        
    async def update(self, unit_id: str, unit: UnitUpdateRequest) -> Unit:
        """
        Update an existing unit.
        
        Args:
            unit_id: Unit ID identifier
            unit: Unit object or dict to update
            
        Returns:
            Updated unit object 
            
        Raises:
            NotFoundError: If unit not found
            MealieAPIError: If the API request fails
        """
        try:
            if hasattr(unit, 'to_dict'):
                unit_data = unit.to_dict()
            else:
                unit_data = unit
            response = await self.client.put(f"units/{unit_id}", json_data=unit_data)
            if isinstance(response, dict):
                return Unit.from_dict(response)
            else:
                return response
        except Exception as e:
            # Handle traditional 404 errors if they occur
            if hasattr(e, 'status_code') and getattr(e, 'status_code') == 404:
                raise NotFoundError(
                    f"Unit '{unit_id}' not found",
                    resource_type="unit",
                    resource_id=unit_id,
                )
            raise 
        
    async def delete(self, unit_id: str) -> bool:
        """
        Delete an existing unit.
        
        Args:
            unit_id: Unit ID identifier
            
        Returns:
            True if deletion was successful
            
        Raises:
            NotFoundError: If unit not found
            MealieAPIError: If the API request fails
        """
        try:
            await self.client.delete(f"units/{unit_id}")
            return True
        except Exception as e:
            # Handle traditional 404 errors if they occur
            if hasattr(e, 'status_code') and getattr(e, 'status_code') == 404:
                raise NotFoundError(
                    f"Unit '{unit_id}' not found",
                    resource_type="unit",
                    resource_id=unit_id,
                )
            raise 
        