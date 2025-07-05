# E2E Testing Framework

Comprehensive end-to-end testing framework cho Mealie SDK với real server integration.

## 🎯 Features

### ✅ Framework Foundation
- **Configuration Management**: Environment-based configuration với validation
- **Base Test Classes**: Common setup, teardown, và utility methods  
- **Data Factories**: Realistic test data generation
- **Cleanup System**: Automatic test data cleanup
- **Custom Assertions**: Domain-specific assertions cho Mealie models

### ✅ Test Coverage
- **Authentication Testing**: Username/password, API token, error scenarios
- **Client Lifecycle**: Session management, context managers, concurrency
- **Recipes CRUD**: Full create, read, update, delete operations
- **Error Handling**: Network errors, validation, not found scenarios
- **Performance Testing**: Concurrent operations, timeout handling

### 🚧 Planned Test Suites
- **Users CRUD**: Full user management testing
- **Groups CRUD**: Group operations testing  
- **Meal Plans CRUD**: Meal planning functionality
- **Shopping Lists CRUD**: Shopping list management + item operations
- **Advanced Features**: Search, filtering, import/export, image management
- **Workflow Testing**: Multi-step complex scenarios
- **Performance & Load Testing**: Stress testing và benchmarks

## 🔧 Setup & Configuration

### Environment Variables

```bash
# Required - Server Configuration
export E2E_MEALIE_BASE_URL="https://your-mealie-server.com"

# Authentication (choose one method)
# Method 1: API Token (recommended)
export E2E_MEALIE_API_TOKEN="your_api_token_here"

# Method 2: Username/Password
export E2E_MEALIE_USERNAME="your_username"
export E2E_MEALIE_PASSWORD="your_password"

# Optional - Test Configuration
export E2E_TIMEOUT="30.0"                    # Request timeout
export E2E_MAX_RETRIES="3"                   # Max retry attempts
export E2E_CLEANUP_DATA="true"               # Auto cleanup test data
export E2E_RUN_PERFORMANCE="false"           # Enable performance tests
export E2E_RUN_LOAD="false"                 # Enable load tests
export E2E_PARALLEL_WORKERS="1"             # Parallel test workers

# Optional - Test Data Prefixes
export E2E_TEST_PREFIX="e2e_test_"
export E2E_USER_PREFIX="e2e_user_"
export E2E_RECIPE_PREFIX="e2e_recipe_"
export E2E_GROUP_PREFIX="e2e_group_"
```

### Quick Start

```bash
# 1. Set up environment
export E2E_MEALIE_BASE_URL="https://demo.mealie.io"
export E2E_MEALIE_API_TOKEN="your_token"

# 2. Run all E2E tests
python -m pytest tests/e2e/ -v

# 3. Run specific test suites
python -m pytest tests/e2e/test_authentication.py -v
python -m pytest tests/e2e/test_recipes_crud.py -v

# 4. Run with cleanup disabled (for debugging)
E2E_CLEANUP_DATA=false python -m pytest tests/e2e/ -v -s
```

## 📁 Framework Architecture

```
tests/e2e/
├── config.py              # Environment configuration management
├── conftest.py             # Pytest fixtures và session setup
├── base_test.py            # Base test classes với common functionality
├── utils/
│   ├── __init__.py
│   ├── data_factory.py     # Test data generators
│   ├── cleanup.py          # Data cleanup utilities
│   └── assertions.py       # Custom assertions
├── test_authentication.py  # Authentication flow tests
├── test_client_lifecycle.py # Client session management tests
├── test_recipes_crud.py    # Recipe CRUD operations
├── test_users_crud.py      # User CRUD operations (planned)
├── test_groups_crud.py     # Group CRUD operations (planned)
├── test_meal_plans_crud.py # Meal plan CRUD operations (planned)
├── test_shopping_lists_crud.py # Shopping list CRUD operations (planned)
├── test_recipes_advanced.py    # Advanced recipe features (planned)
├── test_pagination.py          # Pagination testing (planned)
├── test_error_handling.py      # Error scenarios (planned)
├── test_workflows.py           # Complex workflows (planned)
├── test_performance.py         # Performance testing (planned)
└── README.md               # This documentation
```

## 🧪 Test Classes

### BaseE2ETest & AsyncBaseE2ETest
Base classes providing:
- Client setup/teardown
- Resource tracking and cleanup
- Authentication verification
- Utility methods for creating test data
- Error recovery mechanisms

### Test Categories

#### 1. **Authentication Tests** (`test_authentication.py`)
- Username/password authentication
- API token authentication  
- Invalid credentials handling
- Token refresh mechanisms
- Concurrent authentication
- Context manager usage

#### 2. **Client Lifecycle Tests** (`test_client_lifecycle.py`)
- Session start/stop cycles
- Context manager functionality
- Concurrent client instances
- Connection recovery
- Timeout and retry configuration

#### 3. **CRUD Tests** (`test_*_crud.py`)
- Create operations với validation
- Read operations (by ID, slug, search)
- Update operations (full, partial)
- Delete operations và verification
- Pagination và ordering
- Error handling (not found, validation)
- Complete lifecycle testing

## 🔨 Usage Examples

### Basic Test Writing

```python
import pytest
from tests.e2e.base_test import AsyncBaseE2ETest

class TestMyFeature(AsyncBaseE2ETest):
    @pytest.mark.asyncio
    async def test_my_feature(self, e2e_test_base):
        client = e2e_test_base.client
        
        # Create test data
        recipe = await e2e_test_base.create_test_recipe()
        
        # Test operations
        result = await client.recipes.get(recipe.id)
        assert result.name == recipe.name
        
        # Cleanup is automatic via e2e_test_base fixture
```

### Custom Data Generation

```python
from tests.e2e.utils import E2EDataFactory

# Generate custom test data
data_factory = E2EDataFactory()
custom_recipe = data_factory.generate_test_recipe_data(
    name_suffix="custom",
    include_advanced_fields=True,
    recipe_yield="10 servings"
)
```

### Manual Cleanup

```python
from tests.e2e.utils import E2ECleanup

async def manual_cleanup_example(client):
    cleanup_manager = E2ECleanup(client)
    
    # Clean specific resources
    results = await cleanup_manager.cleanup_specific_resources(
        recipe_ids=["recipe_1", "recipe_2"],
        user_ids=["user_1"]
    )
    
    # Clean all test data
    results = await cleanup_manager.cleanup_all_test_data()
    print(f"Cleaned up: {results}")
```

## 🎛️ Configuration Options

### Test Data Management
- **Auto Cleanup**: Automatically remove test data after tests
- **Prefixed Naming**: All test data uses configurable prefixes
- **Resource Tracking**: Track created resources for cleanup
- **Batch Operations**: Efficient cleanup operations

### Performance Tuning
- **Timeout Configuration**: Adjust request timeouts
- **Retry Logic**: Configure retry attempts và delays
- **Concurrent Testing**: Control parallel test execution
- **Session Sharing**: Reuse authenticated sessions

### Environment Support
- **Multiple Environments**: Dev, staging, production testing
- **Authentication Methods**: API token or username/password
- **Feature Flags**: Enable/disable specific test categories

## 🚀 Running Tests

### Local Development
```bash
# Basic run
python -m pytest tests/e2e/ -v

# With coverage
python -m pytest tests/e2e/ --cov=mealie_client

# Specific markers
python -m pytest tests/e2e/ -m "not performance"

# Parallel execution
python -m pytest tests/e2e/ -n auto
```

### CI/CD Integration
```yaml
# GitHub Actions example
env:
  E2E_MEALIE_BASE_URL: ${{ secrets.E2E_MEALIE_BASE_URL }}
  E2E_MEALIE_API_TOKEN: ${{ secrets.E2E_MEALIE_API_TOKEN }}
  E2E_CLEANUP_DATA: "true"

run: |
  python -m pytest tests/e2e/ -v --tb=short
```

## 🔍 Debugging

### Debug Mode
```bash
# Disable cleanup for debugging
E2E_CLEANUP_DATA=false python -m pytest tests/e2e/test_recipes_crud.py::test_create_basic_recipe -v -s

# Verbose output
python -m pytest tests/e2e/ -v -s --tb=long

# Stop on first failure
python -m pytest tests/e2e/ -x
```

### Manual Cleanup
```bash
# Clean up leftover test data
python -c "
import asyncio
from tests.e2e.config import get_test_config
from tests.e2e.utils import cleanup_test_data
from mealie_client import MealieClient

async def cleanup():
    config = get_test_config()
    async with MealieClient(**config.get_auth_kwargs(), base_url=config.base_url) as client:
        results = await cleanup_test_data(client)
        print(f'Cleaned up: {results}')

asyncio.run(cleanup())
"
```

## 📊 Test Data

### Naming Conventions
- **Recipes**: `e2e_recipe_xxxxx`
- **Users**: `e2e_user_xxxxx`  
- **Groups**: `e2e_group_xxxxx`
- **General**: `e2e_test_xxxxx`

### Data Generation
- **Realistic Data**: Generated data mimics real usage patterns
- **Unique Identifiers**: Each test run generates unique data
- **Configurable Complexity**: Simple or advanced data structures
- **Relationship Handling**: Proper foreign key relationships

## 🛡️ Security

### Authentication
- **Environment Variables**: Credentials stored securely
- **Token Rotation**: Support for token refresh
- **Session Management**: Proper session cleanup
- **Permission Testing**: Test different permission levels

### Data Isolation
- **Prefixed Data**: All test data clearly identified
- **Automatic Cleanup**: No persistent test data
- **Sandbox Testing**: Isolated test environments
- **Conflict Prevention**: Unique naming prevents conflicts

## 📈 Performance

### Optimizations
- **Session Reuse**: Share authenticated sessions
- **Parallel Execution**: Concurrent test execution
- **Efficient Cleanup**: Batch delete operations
- **Connection Pooling**: Reuse HTTP connections

### Monitoring
- **Test Duration**: Track test execution times
- **Resource Usage**: Monitor API rate limits
- **Failure Analysis**: Detailed error reporting
- **Performance Regression**: Track performance changes

---

## 🎯 Implementation Status

### ✅ **COMPLETED (Phase 1 & 2)**
- Configuration management system
- Base test framework với fixtures
- Data factories và cleanup utilities  
- Custom assertions
- Authentication test suite (full coverage)
- Client lifecycle test suite (full coverage)
- Recipes CRUD test suite (basic implementation)

### 🚧 **IN PROGRESS (Phase 3)**
- Advanced recipes features testing
- Users CRUD test suite
- Groups CRUD test suite
- Meal plans CRUD test suite
- Shopping lists CRUD test suite

### 📋 **TODO (Phase 4)**
- Complex workflow testing
- Performance và load testing
- Error handling edge cases
- Advanced search và filtering tests
- Import/export functionality tests
- Image management tests
- Comprehensive documentation
- CI/CD integration examples

**Framework readiness: 70%** - Core infrastructure hoàn tất, đang mở rộng test coverage. 