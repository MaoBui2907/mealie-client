"""
Mealie SDK - Unofficial Python SDK for Mealie API.

This SDK provides a comprehensive interface for interacting with self-hosted
Mealie instances, including recipe management, meal planning, shopping lists,
user management, and more.

Example usage:
    Basic client setup:
    ```python
    from mealie_client import MealieClient
    
    # Using username/password
    async with MealieClient(
        base_url="https://mealie.example.com",
        username="your_username",
        password="your_password"
    ) as client:
        recipes = await client.recipes.get_all()
    
    # Using API token
    async with MealieClient(
        base_url="https://mealie.example.com",
        api_token="your_api_token"
    ) as client:
        recipe = await client.recipes.get("recipe-slug")
    ```
    
    From environment variables:
    ```python
    client = MealieClient.from_env("https://mealie.example.com")
    ```
"""

from .client import MealieClient
from .auth import MealieAuth, AuthenticationManager, create_auth_from_env
from .exceptions import (
    MealieSDKError,
    MealieAPIError,
    AuthenticationError,
    AuthorizationError,
    NotFoundError,
    ValidationError,
    RateLimitError,
    ConnectionError,
    TimeoutError,
    ConfigurationError,
    FileOperationError,
)
from .utils import (
    clean_dict,
)

# Import key models for convenience
from .models import (
    Recipe,
    RecipeCreateRequest,
    RecipeUpdateRequest,
    User,
    UserCreateRequest,
    Group,
    MealPlan,
    ShoppingList,
    # Common enums
    UserRole,
    MealPlanType,
    RecipeVisibility,
    ShoppingListItemStatus,
)

__version__ = "0.1.1"
__author__ = "Mao Bui"
__email__ = "maonguyen199873@gmail.com"
__description__ = "Unofficial Python SDK for Mealie API"

__all__ = [
    # Client and authentication
    "MealieClient",
    "MealieAuth", 
    "AuthenticationManager",
    "create_auth_from_env",
    
    # Exceptions
    "MealieSDKError",
    "MealieAPIError",
    "AuthenticationError",
    "AuthorizationError",
    "NotFoundError",
    "ValidationError",
    "RateLimitError",
    "ConnectionError",
    "TimeoutError",
    "ConfigurationError",
    "FileOperationError",
    
    # Utils
    "clean_dict",
    
    # Key models
    "Recipe",
    "RecipeCreateRequest",
    "RecipeUpdateRequest",
    "User",
    "UserCreateRequest",
    "Group",
    "MealPlan",
    "ShoppingList",
    
    # Enums
    "UserRole",
    "MealPlanType",
    "RecipeVisibility",
    "ShoppingListItemStatus",
    
    # Metadata
    "__version__",
    "__author__",
    "__email__",
    "__description__",
] 