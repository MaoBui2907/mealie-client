"""
Labels endpoint manager for the Mealie SDK.

Labels in Mealie are read-only via API. Create, update, and delete operations
must be performed through the web interface.
"""

from typing import Any, List, Optional

from ..exceptions import NotFoundError
from ..models.common import OrderByNullPosition, OrderDirection
from ..models.label import Label, LabelCreateRequest, LabelFilter, LabelUpdateRequest


class LabelsManager:
    """Manages label-related API operations.
    
    Note: Labels are read-only via Mealie API. CRUD operations are not supported
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
        accept_language: Optional[str] = None,) -> List[Label]:
        """
        Get all labels. (Admin only)
        
        Returns:
            List of label summaries
            
        Raises:
            MealieAPIError: If the API request fails
        """
        response = await self.client.get("groups/labels", params=LabelFilter(
            page=page,
            per_page=per_page,
            order_by=order_by,
            order_direction=order_direction,
            order_by_null_position=order_by_null_position,
            search=search,
            accept_language=accept_language,
        ).to_params())
        
        if isinstance(response, list):
            labels_data = response
            metadata = {
                "page": page,
                "per_page": per_page,
                "total": len(response),
                "total_pages": page,
            }
        elif isinstance(response, dict) and "items" in response:
            labels_data = response["items"]
            metadata = {
                "page": response.get("page", page),
                "per_page": response.get("perPage", per_page),
                "total": response.get("total", 0),
                "total_pages": response.get("totalPages", 0),
            }
        else:
            labels_data = []
            metadata = {
                "page": page,
                "per_page": per_page,
                "total": 0,
                "total_pages": 0,
            }

        return [
            Label.from_dict(label_data) if isinstance(label_data, dict) else label_data
            for label_data in labels_data
        ]

    async def get(self, label_id: str) -> Label:
        """
        Get a specific label by ID. (Admin only)
        
        Args:
            label_id: Label ID identifier
            
        Returns:
            Complete label object
            
        Raises:
            NotFoundError: If label not found
            MealieAPIError: If the API request fails
        """
        try:
            response = await self.client.get(f"groups/labels/{label_id}")
            
            if isinstance(response, bytes):
                response_text = response.decode('utf-8', errors='ignore').lower()
                if '<!doctype html>' in response_text or '<html' in response_text:
                    raise NotFoundError(
                        f"Label '{label_id}' not found",
                        resource_type="label",
                        resource_id=label_id,
                    )
            
            if not isinstance(response, dict):
                raise ValueError("Response must be a dictionary")
            
            return Label.from_dict(response)
        except Exception as e:
            if hasattr(e, 'status_code') and getattr(e, 'status_code') == 404:
                raise NotFoundError(
                    f"Label '{label_id}' not found",
                    resource_type="label",
                    resource_id=label_id,
                )
            raise 
    
    async def create(self, label: LabelCreateRequest) -> Label:
        """
        Create a new label. (Admin only)
        
        Args:
            label: Label object to create
            
        Returns:
            Created label object
            
        Raises:
            MealieAPIError: If the API request fails
        """
        if hasattr(label, 'to_dict'):
            label_data = label.to_dict()
        else:
            label_data = label
        response = await self.client.post("groups/labels", json_data=label_data)
        if not isinstance(response, dict):
            raise ValueError("Response must be a dictionary")
        
        return Label.from_dict(response)
    
    async def update(self, label_id: str, label: LabelUpdateRequest) -> Label:  
        """
        Update a label. (Admin only)
        
        Args:
            label_id: Label ID identifier
            label: Label object to update
            
        Returns:
            Updated label object
            
        Raises:
            MealieAPIError: If the API request fails
        """
        if hasattr(label, 'to_dict'):
            label_data = label.to_dict()
        else:
            label_data = label
        
        if not isinstance(label_data, dict):
            raise ValueError("Label data must be a dictionary")
        
        response = await self.client.put(f"groups/labels/{label_id}", json_data={
            **label_data,
            "id": label_id,
        })
        if not isinstance(response, dict):
            raise ValueError("Response must be a dictionary")
        
        return Label.from_dict(response)
    
    async def delete(self, label_id: str) -> bool:
        """
        Delete a label. (Admin only)
        
        Args:
            label_id: Label ID identifier
            
        Returns:
            True if label was deleted, False otherwise
            
        Raises:
            MealieAPIError: If the API request fails
        """
        response = await self.client.delete(f"groups/labels/{label_id}")
        return response