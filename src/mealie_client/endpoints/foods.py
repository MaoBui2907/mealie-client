"""
Foods endpoint manager for the Mealie SDK.

This module provides comprehensive food management functionality including
CRUD operations, searching, filtering, and food-specific features.

"""

from typing import Any, List, Optional

from ..models.common import OrderByNullPosition, OrderDirection
from ..models.food import Food, FoodCreateRequest, FoodFilter, FoodSummary, FoodUpdateRequest
from ..exceptions import NotFoundError


class FoodsManager:
    """Manages food-related API operations.

    This module provides comprehensive food management functionality including
    CRUD operations, searching, filtering, and food-specific features.

    """

    def __init__(self, client: Any) -> None:
        self.client = client

    async def get_all(self,
        page: int = 1,
        per_page: int = 50,
        order_by: Optional[str] = None,
        order_direction: OrderDirection = OrderDirection.ASC,
        order_by_null_position: OrderByNullPosition = OrderByNullPosition.LAST,
        search: Optional[str] = None,
        accept_language: Optional[str] = None,) -> List[FoodSummary]:
        """
        Get all foods.
        
        Args:
            page: Page number (ignored, for API compatibility)
            per_page: Items per page (ignored, for API compatibility)
        
        Returns:
            List of food summaries
            
        Raises:
            MealieAPIError: If the API request fails
        """
        response = await self.client.get("foods", params=FoodFilter(
            page=page,
            per_page=per_page,
            order_by=order_by,
            order_direction=order_direction,
            order_by_null_position=order_by_null_position,
            search=search,
            accept_language=accept_language,
        ).to_params())
        
        if isinstance(response, list):
            foods_data = response
            metadata = {
                "page": page,
                "per_page": per_page,
                "total": len(response),
                "total_pages": page,
            }
        elif isinstance(response, dict) and "items" in response:
            foods_data = response["items"]
            metadata = {
                "page": response.get("page", page),
                "per_page": response.get("perPage", per_page),
                "total": response.get("total", 0),
                "total_pages": response.get("totalPages", 0),
            }
        else:
            foods_data = []
            metadata = {
                "page": page,
                "per_page": per_page,
                "total": 0,
                "total_pages": 0,
            }

        return [
            FoodSummary.from_dict(food_data) if isinstance(food_data, dict) else food_data
            for food_data in foods_data
        ]

    async def get(self, food_id: str) -> Food:
        """
        Get a specific food by ID.
        
        Args:
            food_id: Food ID identifier
            
        Returns:
            Complete food object
            
        Raises:
            NotFoundError: If food not found
            MealieAPIError: If the API request fails
        """
        try:
            response = await self.client.get(f"foods/{food_id}")
            
            # Mealie API returns HTML content instead of JSON 404 for non-existent foods
            # This is a quirk of how Mealie handles routing - it falls back to the web interface
            if isinstance(response, bytes):
                # Check if it's HTML content (indicates food not found)
                response_text = response.decode('utf-8', errors='ignore').lower()
                if '<!doctype html>' in response_text or '<html' in response_text:
                    raise NotFoundError(
                        f"Food '{food_id}' not found",
                        resource_type="food",
                        resource_id=food_id,
                    )
            
            if not isinstance(response, dict):
                raise ValueError("Response must be a dictionary")
            
            return Food.from_dict(response)
        except Exception as e:
            # Handle traditional 404 errors if they occur
            if hasattr(e, 'status_code') and getattr(e, 'status_code') == 404:
                raise NotFoundError(
                    f"Food '{food_id}' not found",
                    resource_type="food",
                    resource_id=food_id,
                )
            raise 
        
    async def create(self, food: FoodCreateRequest) -> Food:
        """
        Create a new food.
        
        Args:
            food: Food object or dict to create
            
        Returns:
            Created food object 
            
        Raises:
            MealieAPIError: If the API request fails
        """
        if hasattr(food, 'to_dict'):
            food_data = food.to_dict()
        else:
            food_data = food
        response = await self.client.post("foods", json_data=food_data)
        if isinstance(response, dict):
            return Food.from_dict(response)
        else:
            return response
        
    async def update(self, food_id: str, food: FoodUpdateRequest) -> Food:
        """
        Update an existing food.
        
        Args:
            food_id: Food ID identifier
            food: Food object or dict to update
            
        Returns:
            Updated food object 
            
        Raises:
            NotFoundError: If food not found
            MealieAPIError: If the API request fails
        """
        try:
            if hasattr(food, 'to_dict'):
                food_data = food.to_dict()
            else:
                food_data = food

            if not isinstance(food_data, dict):
                raise ValueError("Food data must be a dictionary")
            
            response = await self.client.put(f"foods/{food_id}", json_data={
                **food_data,
                "id": food_id,
            })
            if not isinstance(response, dict):
                raise ValueError("Response must be a dictionary")
            
            return Food.from_dict(response)
        except Exception as e:
            # Handle traditional 404 errors if they occur
            if hasattr(e, 'status_code') and getattr(e, 'status_code') == 404:
                raise NotFoundError(
                    f"Food '{food_id}' not found",
                    resource_type="food",
                    resource_id=food_id,
                )
            raise 
        
    async def delete(self, food_id: str) -> bool:
        """
        Delete an existing food.
        
        Args:
            food_id: Food ID identifier
            
        Returns:
            True if deletion was successful
            
        Raises:
            NotFoundError: If food not found
            MealieAPIError: If the API request fails
        """
        try:
            await self.client.delete(f"foods/{food_id}")
            return True
        except Exception as e:
            # Handle traditional 404 errors if they occur
            if hasattr(e, 'status_code') and getattr(e, 'status_code') == 404:
                raise NotFoundError(
                    f"Food '{food_id}' not found",
                    resource_type="food",
                    resource_id=food_id,
                )
            raise 