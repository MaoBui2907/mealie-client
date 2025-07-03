# Mealie SDK

[![PyPI version](https://badge.fury.io/py/mealie-sdk.svg)](https://badge.fury.io/py/mealie-sdk)
[![Python Support](https://img.shields.io/pypi/pyversions/mealie-sdk.svg)](https://pypi.org/project/mealie-sdk/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

An unofficial Python SDK for [Mealie](https://github.com/mealie-recipes/mealie) - a self-hosted recipe manager and meal planner with a RestAPI backend.

## 🚀 Features

- **Asynchronous API Client**: Built with `httpx` for high-performance async operations
- **Type Safety**: Full type hints with `pydantic` models for all API responses
- **Comprehensive Coverage**: Support for all major Mealie API endpoints
- **Authentication**: Secure token-based authentication
- **Advanced Filtering**: Rich query capabilities with pagination support
- **Recipe Management**: Full CRUD operations for recipes, meal plans, and shopping lists
- **User Management**: Handle users, groups, and permissions
- **File Operations**: Upload and manage recipe images and assets
- **Error Handling**: Comprehensive error handling with custom exceptions
- **Modern Python**: Support for Python 3.8+ with modern async/await patterns

## 📦 Installation

### Using pip

```bash
pip install mealie-sdk
```

### Using PDM (recommended for development)

```bash
pdm add mealie-sdk
```

### Using Poetry

```bash
poetry add mealie-sdk
```

## 🏁 Quick Start

### Basic Usage

```python
import asyncio
from mealie_sdk import MealieClient

async def main():
    # Initialize the client
    client = MealieClient(
        base_url="https://your-mealie-instance.com",
        api_token="your-api-token"
    )
    
    # Get all recipes
    recipes = await client.recipes.get_all()
    print(f"Found {len(recipes)} recipes")
    
    # Get a specific recipe
    recipe = await client.recipes.get_by_slug("my-favorite-recipe")
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

The SDK supports several authentication methods:

#### API Token Authentication (Recommended)

```python
from mealie_sdk import MealieClient

client = MealieClient(
    base_url="https://your-mealie-instance.com",
    api_token="your-long-lived-api-token"
)
```

#### Username/Password Authentication

```python
from mealie_sdk import MealieClient

async def authenticate():
    client = MealieClient(base_url="https://your-mealie-instance.com")
    
    # Login with username/password
    await client.auth.login("username", "password")
    
    # Now you can use the client
    recipes = await client.recipes.get_all()
    return recipes
```

## 📖 Detailed Usage

### Recipe Management

```python
from mealie_sdk import MealieClient
from mealie_sdk.models import RecipeCreate, RecipeUpdate

async def recipe_operations():
    client = MealieClient(
        base_url="https://your-mealie-instance.com",
        api_token="your-api-token"
    )
    
    # Search recipes with filters
    recipes = await client.recipes.get_all(
        query_filter='tags.name CONTAINS "vegetarian"',
        order_by="created_at",
        order_direction="desc",
        per_page=20
    )
    
    # Get recipe with full details
    recipe = await client.recipes.get_by_slug("pasta-carbonara", load_food=True)
    
    # Update a recipe
    updated_recipe = await client.recipes.update("pasta-carbonara", {
        "description": "Updated description",
        "recipe_yield": "4 servings"
    })
    
    # Upload recipe image
    with open("recipe-image.jpg", "rb") as image_file:
        await client.recipes.upload_image("pasta-carbonara", image_file)
    
    # Delete a recipe
    await client.recipes.delete("old-recipe-slug")
```

### Meal Planning

```python
async def meal_planning():
    client = MealieClient(
        base_url="https://your-mealie-instance.com",
        api_token="your-api-token"
    )
    
    # Get current meal plans
    meal_plans = await client.meal_plans.get_all()
    
    # Create a meal plan
    from datetime import date, timedelta
    
    today = date.today()
    meal_plan = await client.meal_plans.create({
        "date": today.isoformat(),
        "entry_type": "breakfast",
        "title": "Healthy Breakfast",
        "recipe_id": "some-recipe-id"
    })
    
    # Get meal plans for a date range
    week_plans = await client.meal_plans.get_all(
        start_date=today,
        end_date=today + timedelta(days=7)
    )
```

### Shopping Lists

```python
async def shopping_operations():
    client = MealieClient(
        base_url="https://your-mealie-instance.com",
        api_token="your-api-token"
    )
    
    # Get all shopping lists
    shopping_lists = await client.shopping_lists.get_all()
    
    # Create a shopping list
    new_list = await client.shopping_lists.create({
        "name": "Weekly Groceries",
        "list_items": [
            {"note": "2 lbs chicken breast"},
            {"note": "1 dozen eggs"},
            {"note": "Vegetables for salad"}
        ]
    })
    
    # Add items to existing list
    await client.shopping_lists.add_item(new_list.id, {
        "note": "Milk - 2% gallon"
    })
```

### User and Group Management

```python
async def user_management():
    client = MealieClient(
        base_url="https://your-mealie-instance.com",
        api_token="your-admin-api-token"  # Admin privileges required
    )
    
    # Get all users
    users = await client.users.get_all()
    
    # Create a new user
    new_user = await client.users.create({
        "username": "newuser",
        "email": "newuser@example.com",
        "password": "secure-password",
        "full_name": "New User"
    })
    
    # Get groups
    groups = await client.groups.get_all()
    
    # Add user to group
    await client.groups.add_user(group_id="group-id", user_id=new_user.id)
```

### Error Handling

```python
from mealie_sdk import MealieClient
from mealie_sdk.exceptions import MealieAPIError, AuthenticationError, NotFoundError

async def error_handling_example():
    client = MealieClient(
        base_url="https://your-mealie-instance.com",
        api_token="your-api-token"
    )
    
    try:
        recipe = await client.recipes.get_by_slug("non-existent-recipe")
    except NotFoundError:
        print("Recipe not found")
    except AuthenticationError:
        print("Invalid authentication credentials")
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
   git clone https://github.com/yourusername/mealie-sdk.git
   cd mealie-sdk
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
pdm run test-unit

# Run integration tests only
pdm run test-integration

# Run with coverage
pdm run test
```

### Code Quality

```bash
# Run linting
pdm run lint

# Format code
pdm run format

# Type checking
pdm run type-check

# Run all pre-commit hooks
pdm run pre-commit
```

### Building Documentation

```bash
# Serve docs locally
pdm run docs-serve

# Build docs
pdm run docs-build
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

### Development Workflow

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for your changes
5. Ensure all tests pass (`pdm run test`)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

### Code Standards

- Follow PEP 8 style guidelines
- Add type hints to all functions and methods
- Write comprehensive docstrings
- Maintain test coverage above 90%
- Use descriptive commit messages

## 📚 API Reference

### Core Classes

- **`MealieClient`**: Main client class for interacting with Mealie API
- **`RecipeManager`**: Handles all recipe-related operations
- **`MealPlanManager`**: Manages meal planning functionality
- **`ShoppingListManager`**: Shopping list operations
- **`UserManager`**: User management (requires admin privileges)
- **`GroupManager`**: Group management (requires admin privileges)

### Models

The SDK includes comprehensive Pydantic models for all Mealie data structures:

- `Recipe`, `RecipeCreate`, `RecipeUpdate`
- `MealPlan`, `MealPlanCreate`, `MealPlanUpdate`
- `ShoppingList`, `ShoppingListCreate`, `ShoppingListUpdate`
- `User`, `UserCreate`, `UserUpdate`
- `Group`, `GroupCreate`, `GroupUpdate`

For detailed API documentation, visit the [full documentation](https://github.com/yourusername/mealie-sdk#documentation).

## 🔧 Configuration

### Environment Variables

You can configure the SDK using environment variables:

```bash
export MEALIE_BASE_URL="https://your-mealie-instance.com"
export MEALIE_API_TOKEN="your-api-token"
```

```python
from mealie_sdk import MealieClient

# Client will automatically use environment variables
client = MealieClient()
```

### Client Configuration

```python
from mealie_sdk import MealieClient

client = MealieClient(
    base_url="https://your-mealie-instance.com",
    api_token="your-api-token",
    timeout=30.0,  # Request timeout in seconds
    verify_ssl=True,  # SSL verification
    retry_attempts=3,  # Number of retry attempts
    retry_delay=1.0,  # Delay between retries
)
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Mealie](https://github.com/mealie-recipes/mealie) - The amazing self-hosted recipe manager that this SDK interfaces with
- [httpx](https://github.com/encode/httpx) - For the excellent async HTTP client
- [Pydantic](https://github.com/pydantic/pydantic) - For robust data validation and serialization

## 📞 Support

- **Documentation**: [GitHub Wiki](https://github.com/yourusername/mealie-sdk/wiki)
- **Issues**: [GitHub Issues](https://github.com/yourusername/mealie-sdk/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/mealie-sdk/discussions)

## 🔗 Related Projects

- [Mealie](https://github.com/mealie-recipes/mealie) - The official Mealie recipe manager
- [Mealie Mobile App](https://github.com/mealie-recipes/mealie-mobile) - Official mobile app for Mealie

---

**Disclaimer**: This is an unofficial SDK and is not affiliated with or endorsed by the Mealie project. Mealie is a trademark of its respective owners. 