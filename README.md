# Mealie Client

[![PyPI version](https://badge.fury.io/py/mealie-client.svg)](https://badge.fury.io/py/mealie-client)
[![Python Support](https://img.shields.io/pypi/pyversions/mealie-client.svg)](https://pypi.org/project/mealie-client/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

An unofficial Python SDK for [Mealie](https://github.com/mealie-recipes/mealie) - a self-hosted recipe manager and meal planner with a RestAPI backend.

## 🚀 Features

- **Asynchronous API Client**: Built with `httpx` for high-performance async operations
- **Type Safety**: Full type hints with `pydantic` models for all API responses
- **Core Endpoints Supported**: Recipes, Users, Groups, Meal Plans, and Shopping Lists
- **Authentication**: Secure token-based authentication and username/password login
- **Recipe Management**: Full CRUD operations, search, filtering, and image management
- **Meal Planning**: Create and manage meal plans with date filtering
- **Shopping Lists**: Complete shopping list and item management
- **Error Handling**: Comprehensive error handling with custom exceptions
- **Modern Python**: Support for Python 3.8+ with modern async/await patterns

## 📈 Current API Coverage

This SDK currently covers the following Mealie API endpoints:

✅ **Recipes** - Create, read, update, delete, search, image upload, import from URL  
✅ **Users** - User management and current user info  
✅ **Groups** - Basic group operations  
✅ **Meal Plans** - Meal planning with date filtering  
✅ **Shopping Lists** - Shopping lists and item management  
✅ **Units** - Unit management
✅ **Foods** - Food management
✅ **Households** - Household management

🔄 **Planned for Future Releases**:
- Categories, Tags, and Tools endpoints
- Recipe Extras (custom metadata)
- Webhooks and Event Subscriptions
- Timeline Events
- Advanced search features

## 📦 Installation

### Using pip

```bash
pip install mealie-client
```

### Using PDM (recommended for development)

```bash
pdm add mealie-client
```

### Using Poetry

```bash
poetry add mealie-client
```

## 🏁 Quick Start

### Basic Usage

```python
import asyncio
from mealie_client import MealieClient

async def main():
    # Initialize the client
    async with MealieClient(
        base_url="https://your-mealie-instance.com",
        api_token="your-api-token"
    ) as client:
        
        # Get all recipes
        recipes = await client.recipes.get_all()
        print(f"Found {len(recipes)} recipes")
        
        # Get a specific recipe
        recipe = await client.recipes.get("recipe-slug-or-id")
        if recipe:
            print(f"Recipe: {recipe.name}")
            print(f"Description: {recipe.description}")
        
        # Create a new recipe
        new_recipe = await client.recipes.create({
            "name": "Test Recipe",
            "description": "A test recipe created via SDK",
            "recipe_ingredient": [
                {"note": "2 cups flour"},
                {"note": "1 cup sugar"}
            ],
            "recipe_instructions": [
                {"text": "Mix flour and sugar"},
                {"text": "Bake at 350°F for 30 minutes"}
            ]
        })
        
        print(f"Created recipe: {new_recipe.name}")

# Run the async function
asyncio.run(main())
```

### Authentication

The SDK supports both API token and username/password authentication:

#### API Token Authentication (Recommended)

```python
from mealie_client import MealieClient

# Using API token
async with MealieClient(
    base_url="https://your-mealie-instance.com",
    api_token="your-long-lived-api-token"
) as client:
    recipes = await client.recipes.get_all()
```

#### Username/Password Authentication

```python
from mealie_client import MealieClient

# Using username/password
async with MealieClient(
    base_url="https://your-mealie-instance.com",
    username="your_username",
    password="your_password"
) as client:
    recipes = await client.recipes.get_all()
```

#### Environment Variables

```python
# Set environment variables
# MEALIE_USERNAME=your_username
# MEALIE_PASSWORD=your_password
# MEALIE_API_TOKEN=your_api_token

from mealie_client import MealieClient

client = MealieClient.from_env("https://your-mealie-instance.com")
```

## 📖 Usage Examples

### Recipe Management

```python
from mealie_client import MealieClient

async def recipe_operations():
    async with MealieClient(
        base_url="https://your-mealie-instance.com",
        api_token="your-api-token"
    ) as client:
        
        # Search recipes with filters
        recipes = await client.recipes.get_all(
            search="pasta",
            categories=["Italian"],
            tags=["quick"],
            per_page=20,
            order_by="created_at",
            order_direction="desc"
        )
        
        # Get recipe details
        recipe = await client.recipes.get("pasta-carbonara")
        
        # Update a recipe
        updated_recipe = await client.recipes.update("pasta-carbonara", {
            "description": "Updated description",
            "prep_time": "PT15M"  # 15 minutes in ISO format
        })
        
        # Upload recipe image
        with open("recipe-image.jpg", "rb") as image_file:
            await client.recipes.upload_image("pasta-carbonara", image_file)
        
        # Import recipe from URL
        imported_recipe = await client.recipes.import_from_url(
            "https://example.com/recipe"
        )
        
        # Delete a recipe
        await client.recipes.delete("old-recipe-slug")
```

### Meal Planning

```python
from datetime import date, timedelta

async def meal_planning():
    async with MealieClient(
        base_url="https://your-mealie-instance.com",
        api_token="your-api-token"
    ) as client:
        
        # Get current meal plans
        today = date.today()
        meal_plans = await client.meal_plans.get_all(
            start_date=today,
            end_date=today + timedelta(days=7)
        )
        
        # Create a meal plan
        meal_plan = await client.meal_plans.create({
            "date": today.isoformat(),
            "entry_type": "dinner",
            "title": "Italian Night",
            "recipe_id": "pasta-carbonara-id"
        })
        
        # Update meal plan
        await client.meal_plans.update(meal_plan.id, {
            "title": "Updated Italian Night"
        })
```

### Shopping Lists

```python
async def shopping_operations():
    async with MealieClient(
        base_url="https://your-mealie-instance.com",
        api_token="your-api-token"
    ) as client:
        
        # Get all shopping lists
        shopping_lists = await client.shopping_lists.get_all()
        
        # Create a shopping list
        new_list = await client.shopping_lists.create({
            "name": "Weekly Groceries",
            "list_items": [
                {"note": "2 lbs chicken breast"},
                {"note": "1 dozen eggs"},
                {"note": "Fresh vegetables"}
            ]
        })
        
        # Add items to existing list
        await client.shopping_lists.add_item(new_list.id, {
            "note": "Milk - 2% gallon"
        })
        
        # Update an item
        await client.shopping_lists.update_item(
            new_list.id, 
            item_id="item-id",
            {"checked": True}
        )
```

### User and Group Management

```python
async def user_management():
    async with MealieClient(
        base_url="https://your-mealie-instance.com",
        api_token="your-admin-api-token"  # Admin privileges required
    ) as client:
        
        # Get current user info
        current_user = await client.users.get_current()
        print(f"Logged in as: {current_user.username}")
        
        # Get all users (admin only)
        users = await client.users.get_all()
        
        # Create a new user (admin only)
        new_user = await client.users.create({
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "secure-password",
            "full_name": "New User"
        })
        
        # Get groups
        groups = await client.groups.get_all()
```

### Error Handling

```python
from mealie_client import MealieClient
from mealie_client.exceptions import (
    MealieAPIError, 
    AuthenticationError, 
    NotFoundError,
    ValidationError
)

async def error_handling_example():
    async with MealieClient(
        base_url="https://your-mealie-instance.com",
        api_token="your-api-token"
    ) as client:
        
        try:
            recipe = await client.recipes.get("non-existent-recipe")
        except NotFoundError:
            print("Recipe not found")
        except AuthenticationError:
            print("Invalid authentication credentials")
        except ValidationError as e:
            print(f"Validation error: {e.validation_errors}")
        except MealieAPIError as e:
            print(f"API Error: {e.message} (Status: {e.status_code})")
```

## 🛠️ Development

### Prerequisites

- Python 3.8+
- PDM (Python Dependency Manager)

### Setup Development Environment

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/mealie-client.git
   cd mealie-client
   ```

2. **Install dependencies**:
   ```bash
   pdm install -G dev
   ```

3. **Set up pre-commit hooks**:
   ```bash
   pdm run pre-commit install
   ```

### Running Tests

```bash
# Run all tests
pdm run test

# Run unit tests only
pdm run pytest tests/unit

# Run integration tests only  
pdm run pytest tests/integration

# Run with coverage
pdm run pytest --cov=src/mealie_client
```

### Code Quality

```bash
# Run linting
pdm run ruff check src tests

# Format code
pdm run black src tests

# Type checking
pdm run mypy src
```

## 🔧 Configuration

### Environment Variables

```bash
export MEALIE_BASE_URL="https://your-mealie-instance.com"
export MEALIE_API_TOKEN="your-api-token"
# OR
export MEALIE_USERNAME="your-username"
export MEALIE_PASSWORD="your-password"
```

### Client Configuration

```python
from mealie_client import MealieClient

client = MealieClient(
    base_url="https://your-mealie-instance.com",
    api_token="your-api-token",
    timeout=30.0,  # Request timeout in seconds
    max_retries=3,  # Number of retry attempts
    retry_delay=1.0,  # Delay between retries
)
```

## 📚 API Reference

### Core Classes

- **`MealieClient`**: Main client class for interacting with Mealie API
- **`RecipesManager`**: Handles all recipe-related operations
- **`MealPlansManager`**: Manages meal planning functionality
- **`ShoppingListsManager`**: Shopping list operations
- **`UsersManager`**: User management
- **`GroupsManager`**: Group management
- **`UnitsManager`**: Unit management
- **`FoodsManager`**: Food management
- **`HouseholdsManager`**: Household management

### Available Models

The SDK includes Pydantic models for all supported data structures:

- `Recipe`, `RecipeCreateRequest`, `RecipeUpdateRequest`, `RecipeSummary`
- `MealPlan`, `MealPlanCreateRequest`, `MealPlanUpdateRequest`
- `ShoppingList`, `ShoppingListItem`, `ShoppingListCreateRequest`
- `User`, `UserCreateRequest`, `UserUpdateRequest`
- `Group`, `GroupSummary`
- `Unit`, `UnitCreateRequest`, `UnitUpdateRequest`, `UnitSummary`
- `Food`, `FoodCreateRequest`, `FoodUpdateRequest`, `FoodSummary`
- `Household`, `HouseholdSummary`

## 🎯 Roadmap

### Version 0.1.0 (Current)
- [x] Recipes management endpoint
- [x] Users management endpoint
- [x] Groups management endpoint
- [x] Meal plans management endpoint
- [x] Shopping lists management endpoint
- [x] Units management endpoint
- [x] Foods management endpoint
- [x] Households management endpoint

### Version 0.2.0 (Planned)
- [ ] Categories, Tags, and Tools endpoints
- [ ] Recipe search improvements
- [ ] Better error messages

### Version 0.3.0 (Planned)
- [ ] Recipe Extras support
- [ ] Webhooks management
- [ ] Timeline Events
- [ ] Advanced filtering options

### Version 0.4.0 (Future)
- [ ] Backup/Restore functionality
- [ ] Bulk operations
- [ ] Enhanced meal plan features
- [ ] Performance optimizations

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Development Workflow

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes and add tests
4. Ensure all tests pass (`pdm run test`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Mealie](https://github.com/mealie-recipes/mealie) - The amazing self-hosted recipe manager
- [httpx](https://github.com/encode/httpx) - For the excellent async HTTP client
- [Pydantic](https://github.com/pydantic/pydantic) - For robust data validation

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/mealie-client/issues)

---

**Disclaimer**: This is an unofficial SDK and is not affiliated with or endorsed by the Mealie project. 