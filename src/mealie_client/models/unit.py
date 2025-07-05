"""
Unit models for the Mealie SDK.

This module contains data models for unit and unit management.
"""

from datetime import datetime
from typing import Any, Dict, List, Literal, Optional, Union

from .common import BaseModel, OrderByNullPosition, convert_datetime, QueryFilter, OrderDirection


class Unit(BaseModel):
    """Complete unit model with settings and preferences."""

    def __init__(
        self,
        id: Optional[str] = None,
        name: str = "",
        pluralName: str = "",
        description: str = "",
        extras: Optional[Dict[str, Any]] = None,
        fraction: bool = False,
        abbreviation: str = "",
        pluralAbbreviation: str = "",
        useAbbreviation: bool = False,
        aliases: Optional[List[str]] = None,
        createdAt: Optional[Union[str, datetime]] = None,
        updatedAt: Optional[Union[str, datetime]] = None,
        **kwargs: Any,
    ) -> None:
        self.id = id
        self.name = name
        self.pluralName = pluralName
        self.description = description
        self.extras = extras or {}
        self.fraction = fraction
        self.abbreviation = abbreviation
        self.pluralAbbreviation = pluralAbbreviation
        self.useAbbreviation = useAbbreviation
        self.aliases = aliases or []
        self.createdAt = convert_datetime(createdAt)
        self.updatedAt = convert_datetime(updatedAt)
        super().__init__(**kwargs)


class UnitCreateRequest(BaseModel):
    """Request model for creating a new unit."""

    def __init__(
        self,
        name: str,
        pluralName: str,
        description: Optional[str] = None,
        extras: Optional[Dict[str, Any]] = None,
        fraction: bool = False,
        abbreviation: str = "",
        pluralAbbreviation: str = "",
        useAbbreviation: bool = False,
        aliases: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> None:
        self.name = name
        self.pluralName = pluralName
        self.description = description
        self.extras = extras or {}
        self.fraction = fraction
        self.abbreviation = abbreviation
        self.pluralAbbreviation = pluralAbbreviation
        self.useAbbreviation = useAbbreviation
        self.aliases = aliases or []
        super().__init__(**kwargs)


class UnitUpdateRequest(BaseModel):
    """Request model for updating unit information."""

    def __init__(
        self,
        name: Optional[str] = None,
        pluralName: Optional[str] = None,
        description: Optional[str] = None,
        extras: Optional[Dict[str, Any]] = None,
        fraction: Optional[bool] = None,
        abbreviation: Optional[str] = None,
        pluralAbbreviation: Optional[str] = None,
        useAbbreviation: Optional[bool] = None,
        aliases: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> None:
        self.name = name
        self.pluralName = pluralName
        self.description = description
        self.extras = extras or {}
        self.fraction = fraction
        self.abbreviation = abbreviation
        self.pluralAbbreviation = pluralAbbreviation
        self.useAbbreviation = useAbbreviation
        self.aliases = aliases or []
        super().__init__(**kwargs)


class UnitSummary(BaseModel):
    """Lightweight unit summary for list views."""

    def __init__(
        self,
        id: Optional[str] = None,
        name: str = "",
        pluralName: str = "",
        description: str = "",
        extras: Optional[Dict[str, Any]] = None,
        fraction: bool = False,
        abbreviation: str = "",
        pluralAbbreviation: str = "",
        useAbbreviation: bool = False,
        aliases: Optional[List[str]] = None,
        createdAt: Optional[Union[str, datetime]] = None,
        updatedAt: Optional[Union[str, datetime]] = None,
        **kwargs: Any,
    ) -> None:
        self.id = id
        self.name = name
        self.pluralName = pluralName
        self.description = description
        self.extras = extras or {}
        self.fraction = fraction
        self.abbreviation = abbreviation
        self.pluralAbbreviation = pluralAbbreviation
        self.useAbbreviation = useAbbreviation
        self.aliases = aliases or []
        self.createdAt = convert_datetime(createdAt)
        self.updatedAt = convert_datetime(updatedAt)
        super().__init__(**kwargs)


class UnitFilter(QueryFilter):
    """Filter options for unit queries."""

    def __init__(
        self,
        page: int = 1,
        per_page: int = 50,
        order_by: Optional[str] = None,
        order_direction: Union[str, OrderDirection] = OrderDirection.ASC,
        order_by_null_position: OrderByNullPosition = OrderByNullPosition.LAST,
        search: Optional[str] = None,
        accept_language: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        # Convert string to OrderDirection if needed
        if isinstance(order_direction, str):
            order_direction = OrderDirection(order_direction)

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