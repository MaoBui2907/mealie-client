"""
Households endpoint manager for the Mealie SDK.

Households in Mealie are read-only via API. Create, update, and delete operations
must be performed through the web interface.
"""

from typing import Any, List, Optional

from ..models.household import Household, HouseholdCreateRequest, HouseholdFilter, HouseholdSummary, HouseholdUpdateRequest
from ..models.common import OrderDirection, OrderByNullPosition
from ..exceptions import NotFoundError


class HouseholdsManager:
    """Manages household-related API operations.
    
    Note: Households are read-only via Mealie API. CRUD operations are not supported
    and must be performed through the web interface.
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
        accept_language: Optional[str] = None,) -> List[HouseholdSummary]:
        """
        Get all households from all groups. (Admin only)
        
        Args:
            page: Page number (ignored, for API compatibility)
            per_page: Items per page (ignored, for API compatibility)
        
        Returns:
            List of household summaries
            
        Raises:
            MealieAPIError: If the API request fails
        """
        response = await self.client.get("admin/households", params=HouseholdFilter(
            page=page,
            per_page=per_page,
            order_by=order_by,
            order_direction=order_direction,
            order_by_null_position=order_by_null_position,
            search=search,
            accept_language=accept_language,
        ).to_params())
        
        if isinstance(response, list):
            households_data = response
        elif isinstance(response, dict) and "items" in response:
            households_data = response["items"]
        else:
            households_data = []

        return [
            HouseholdSummary.from_dict(household_data) if isinstance(household_data, dict) else household_data
            for household_data in households_data
        ]

    async def get(self, household_id: str) -> Household:
        """
        Get a specific household by ID. (Admin only)
        
        Args:
            household_id: Household ID identifier
            
        Returns:
            Complete household object
            
        Raises:
            NotFoundError: If household not found
            MealieAPIError: If the API request fails
        """
        try:
            response = await self.client.get(f"admin/households/{household_id}")
            
            # Mealie API returns HTML content instead of JSON 404 for non-existent groups
            # This is a quirk of how Mealie handles routing - it falls back to the web interface
            if isinstance(response, bytes):
                # Check if it's HTML content (indicates group not found)
                response_text = response.decode('utf-8', errors='ignore').lower()
                if '<!doctype html>' in response_text or '<html' in response_text:
                    raise NotFoundError(
                        f"Household '{household_id}' not found",
                        resource_type="household",
                        resource_id=household_id,
                    )
            
            if not isinstance(response, dict):
                raise ValueError("Response must be a dictionary")
            
            return Household.from_dict(response) if isinstance(response, dict) else response
        except Exception as e:
            # Handle traditional 404 errors if they occur
            if hasattr(e, 'status_code') and getattr(e, 'status_code') == 404:
                raise NotFoundError(
                    f"Household '{household_id}' not found",
                    resource_type="household",
                    resource_id=household_id,
                )
            raise 
    
    async def create(self, household: HouseholdCreateRequest) -> Household:
        """
        Create a new household. (Admin only)
        """
        if hasattr(household, "to_dict"):
            household_data = household.to_dict()
        else:
            household_data = household
        
        response = await self.client.post("admin/households", json_data=household_data)
        return Household.from_dict(response)

    async def update(self, household_id: str, household: HouseholdUpdateRequest) -> Household:
        """
        Update a household. (Admin only)
        """
        if hasattr(household, "to_dict"):
            household_data = household.to_dict()
        else:
            household_data = household
        
        response = await self.client.put(f"admin/households/{household_id}", json_data=household_data)
        return Household.from_dict(response)
    
    async def delete(self, household_id: str) -> bool:
        """
        Delete a household. (Admin only)
        """
        response = await self.client.delete(f"admin/households/{household_id}")
        return response.status_code == 200

    async def get_self(self) -> Household:
        """
        Get the current user's household.
        """
        response = await self.client.get("households/self")
        return Household.from_dict(response)