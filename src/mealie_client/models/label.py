"""
Label models for the Mealie SDK.

This module contains data models for labels.
"""

from .common import BaseModel, OrderByNullPosition, OrderDirection, QueryFilter 
from typing import Any, Optional

class Label(BaseModel):
    """Label."""
    
    def __init__(
        self,
        id: Optional[str] = None,
        name: str = "",
        color: Optional[str] = None,
        group_id: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        self.id = id
        self.name = name
        self.color = color
        self.group_id = group_id
        super().__init__(**kwargs)

class LabelCreateRequest(BaseModel):
    """Request model for creating a label."""
    
    def __init__(
        self,
        name: str,
        color: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        self.name = name
        self.color = color
        super().__init__(**kwargs)

class LabelUpdateRequest(BaseModel):
    """Request model for updating a label."""
    
    def __init__(
        self,
        name: Optional[str] = None,
        color: Optional[str] = None,
        group_id: Optional[str] = None,
        id: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        self.name = name
        self.color = color
        self.group_id = group_id
        self.id = id
        super().__init__(**kwargs)

class LabelFilter(QueryFilter):
    """Filter options for label queries."""
    
    def __init__(
        self,
        page: int = 1,
        per_page: int = 50,
        order_by: Optional[str] = None,
        order_direction: OrderDirection = OrderDirection.ASC,
        order_by_null_position: OrderByNullPosition = OrderByNullPosition.LAST,
        search: Optional[str] = None,
        accept_language: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            page=page,
            per_page=per_page,
            order_by=order_by,
            order_direction=order_direction,
            order_by_null_position=order_by_null_position,
            search=search,
            accept_language=accept_language,
            **kwargs,
        )