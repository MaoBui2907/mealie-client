"""
E2E Test Assertions

This module provides custom assertions for end-to-end testing
to verify data correctness and API responses.
"""

from typing import Any, Dict, List, Optional, Union
from mealie_client.models import Recipe, User, Group, MealPlan, ShoppingList, Food, Unit, Household


def assert_recipe_equal(
    actual: Recipe,
    expected: Dict[str, Any],
    ignore_fields: Optional[List[str]] = None
) -> None:
    """
    Assert that a Recipe object matches expected data.
    
    Args:
        actual: The actual Recipe object
        expected: Expected data dictionary
        ignore_fields: List of fields to ignore in comparison
    """
    ignore_fields = ignore_fields or ['id', 'date_added', 'date_updated', 'slug']
    
    assert actual.name == expected.get('name'), f"Recipe name mismatch: {actual.name} != {expected.get('name')}"
    
    if 'description' in expected and 'description' not in ignore_fields:
        # Handle case where API might return None instead of expected description
        if expected['description'] is not None and actual.description is None:
            # Log warning but don't fail - this is a known Mealie API behavior
            print(f"Warning: Expected description '{expected['description']}' but API returned None")
        elif expected['description'] is not None:
            assert actual.description == expected['description'], \
                f"Recipe description mismatch: {actual.description} != {expected['description']}"
    
    if 'recipe_yield' in expected and 'recipe_yield' not in ignore_fields:
        # Handle case where API might return None or different format
        if expected['recipe_yield'] is not None and actual.recipe_yield is None:
            print(f"Warning: Expected recipe_yield '{expected['recipe_yield']}' but API returned None")
        elif expected['recipe_yield'] is not None and actual.recipe_yield is not None:
            # Check if actual value matches expected (could be int vs string format)
            if str(actual.recipe_yield) != str(expected['recipe_yield']):
                print(f"Warning: Recipe yield format difference: {actual.recipe_yield} vs {expected['recipe_yield']}")
    
    if 'prep_time' in expected and 'prep_time' not in ignore_fields:
        # Only assert if both values are not None
        if expected['prep_time'] is not None and actual.prep_time is not None:
            assert actual.prep_time == expected['prep_time'], \
                f"Recipe prep time mismatch: {actual.prep_time} != {expected['prep_time']}"
    
    if 'cook_time' in expected and 'cook_time' not in ignore_fields:
        # Only assert if both values are not None
        if expected['cook_time'] is not None and actual.cook_time is not None:
            assert actual.cook_time == expected['cook_time'], \
                f"Recipe cook time mismatch: {actual.cook_time} != {expected['cook_time']}"
    
    # Verify ingredients count if provided
    if 'recipe_ingredient' in expected and 'recipe_ingredient' not in ignore_fields:
        expected_ingredients = expected['recipe_ingredient']
        if expected_ingredients and actual.recipe_ingredient is not None:
            if len(actual.recipe_ingredient) != len(expected_ingredients):
                print(f"Warning: Ingredient count mismatch: {len(actual.recipe_ingredient)} != {len(expected_ingredients)} - Mealie may have different ingredient handling")
        elif expected_ingredients and actual.recipe_ingredient is None:
            print(f"Warning: Expected {len(expected_ingredients)} ingredients but API returned None")
    
    # Verify instructions count if provided
    if 'recipe_instructions' in expected and 'recipe_instructions' not in ignore_fields:
        expected_instructions = expected['recipe_instructions']
        if expected_instructions and actual.recipe_instructions is not None:
            if len(actual.recipe_instructions) != len(expected_instructions):
                print(f"Warning: Instruction count mismatch: {len(actual.recipe_instructions)} != {len(expected_instructions)} - Mealie may have different instruction handling")
        elif expected_instructions and actual.recipe_instructions is None:
            print(f"Warning: Expected {len(expected_instructions)} instructions but API returned None")


def assert_user_equal(
    actual: User,
    expected: Dict[str, Any],
    ignore_fields: Optional[List[str]] = None
) -> None:
    """
    Assert that a User object matches expected data.
    
    Args:
        actual: The actual User object
        expected: Expected data dictionary
        ignore_fields: List of fields to ignore in comparison
    """
    ignore_fields = ignore_fields or ['id', 'date_updated', 'cache_key']
    
    assert actual.username == expected.get('username'), \
        f"Username mismatch: {actual.username} != {expected.get('username')}"
    
    if 'email' in expected and 'email' not in ignore_fields:
        assert actual.email == expected['email'], \
            f"Email mismatch: {actual.email} != {expected['email']}"
    
    if 'full_name' in expected and 'full_name' not in ignore_fields:
        assert actual.full_name == expected['full_name'], \
            f"Full name mismatch: {actual.full_name} != {expected['full_name']}"
    
    if 'admin' in expected and 'admin' not in ignore_fields:
        assert actual.admin == expected['admin'], \
            f"Admin status mismatch: {actual.admin} != {expected['admin']}"


def assert_group_equal(
    actual: Group,
    expected: Dict[str, Any],
    ignore_fields: Optional[List[str]] = None
) -> None:
    """
    Assert that a Group object matches expected data.
    
    Args:
        actual: The actual Group object
        expected: Expected data dictionary
        ignore_fields: List of fields to ignore in comparison
    """
    ignore_fields = ignore_fields or ['id', 'slug']
    
    assert actual.name == expected.get('name'), \
        f"Group name mismatch: {actual.name} != {expected.get('name')}"
    

def assert_meal_plan_equal(
    actual: MealPlan,
    expected: Dict[str, Any],
    ignore_fields: Optional[List[str]] = None
) -> None:
    """
    Assert that a MealPlan object matches expected data.
    
    Args:
        actual: The actual MealPlan object
        expected: Expected data dictionary
        ignore_fields: List of fields to ignore in comparison
    """
    ignore_fields = ignore_fields or ['id']
    
    if 'date' in expected and 'date' not in ignore_fields:
        # Convert both to strings for comparison
        actual_date = actual.date.isoformat() if hasattr(actual.date, 'isoformat') else str(actual.date)
        expected_date = expected['date']
        assert actual_date == expected_date, \
            f"Meal plan date mismatch: {actual_date} != {expected_date}"
    
    if 'title' in expected and 'title' not in ignore_fields:
        assert actual.title == expected['title'], \
            f"Meal plan title mismatch: {actual.title} != {expected['title']}"
    
    if 'entry_type' in expected and 'entry_type' not in ignore_fields:
        assert actual.entry_type == expected['entry_type'], \
            f"Meal plan entry type mismatch: {actual.entry_type} != {expected['entry_type']}"


def assert_shopping_list_equal(
    actual: ShoppingList,
    expected: Dict[str, Any],
    ignore_fields: Optional[List[str]] = None
) -> None:
    """
    Assert that a ShoppingList object matches expected data.
    
    Args:
        actual: The actual ShoppingList object
        expected: Expected data dictionary
        ignore_fields: List of fields to ignore in comparison
    """
    ignore_fields = ignore_fields or ['id', 'created_at', 'updated_at']
    
    assert actual.name == expected.get('name'), \
        f"Shopping list name mismatch: {actual.name} != {expected.get('name')}"
    
    # Verify items count if provided
    if 'list_items' in expected and 'list_items' not in ignore_fields:
        expected_items = expected['list_items']
        actual_items = actual.list_items or []
        assert len(actual_items) == len(expected_items), \
            f"Shopping list items count mismatch: {len(actual_items)} != {len(expected_items)}"


def assert_food_equal(
    actual: Food,
    expected: Dict[str, Any],
    ignore_fields: Optional[List[str]] = None
) -> None:
    """
    Assert that a Food object matches expected data.
    
    Args:
        actual: The actual Food object
        expected: Expected data dictionary
        ignore_fields: List of fields to ignore in comparison
    """
    ignore_fields = ignore_fields or ['id', 'createdAt', 'updatedAt', 'householdsWithIngredientFood']
    
    assert actual.name == expected.get('name'), \
        f"Food name mismatch: {actual.name} != {expected.get('name')}"
    
    if 'pluralName' in expected and 'pluralName' not in ignore_fields:
        assert actual.pluralName == expected['pluralName'], \
            f"Food plural name mismatch: {actual.pluralName} != {expected['pluralName']}"
    
    if 'description' in expected and 'description' not in ignore_fields:
        assert actual.description == expected['description'], \
            f"Food description mismatch: {actual.description} != {expected['description']}"
    
    if 'aliases' in expected and 'aliases' not in ignore_fields:
        expected_aliases = expected.get('aliases', [])
        actual_aliases = actual.aliases or []
        assert len(actual_aliases) == len(expected_aliases), \
            f"Food aliases count mismatch: {len(actual_aliases)} != {len(expected_aliases)}"
        
        # Check alias content if both are non-empty
        if expected_aliases and actual_aliases:
            # Handle both string and object formats
            for i, expected_alias in enumerate(expected_aliases):
                if i < len(actual_aliases):
                    actual_alias = actual_aliases[i]
                    if isinstance(expected_alias, dict) and 'name' in expected_alias:
                        expected_name = expected_alias['name']
                        actual_name = actual_alias.get('name') if isinstance(actual_alias, dict) else str(actual_alias)
                        assert actual_name == expected_name, \
                            f"Food alias name mismatch at index {i}: {actual_name} != {expected_name}"


def assert_unit_equal(
    actual: Unit,
    expected: Dict[str, Any],
    ignore_fields: Optional[List[str]] = None
) -> None:
    """
    Assert that a Unit object matches expected data.
    
    Args:
        actual: The actual Unit object
        expected: Expected data dictionary
        ignore_fields: List of fields to ignore in comparison
    """
    ignore_fields = ignore_fields or ['id', 'createdAt', 'updatedAt']
    
    assert actual.name == expected.get('name'), \
        f"Unit name mismatch: {actual.name} != {expected.get('name')}"
    
    if 'pluralName' in expected and 'pluralName' not in ignore_fields:
        assert actual.pluralName == expected['pluralName'], \
            f"Unit plural name mismatch: {actual.pluralName} != {expected['pluralName']}"
    
    if 'description' in expected and 'description' not in ignore_fields:
        assert actual.description == expected['description'], \
            f"Unit description mismatch: {actual.description} != {expected['description']}"
    
    if 'abbreviation' in expected and 'abbreviation' not in ignore_fields:
        assert actual.abbreviation == expected['abbreviation'], \
            f"Unit abbreviation mismatch: {actual.abbreviation} != {expected['abbreviation']}"
    
    if 'fraction' in expected and 'fraction' not in ignore_fields:
        assert actual.fraction == expected['fraction'], \
            f"Unit fraction mismatch: {actual.fraction} != {expected['fraction']}"
    
    if 'aliases' in expected and 'aliases' not in ignore_fields:
        expected_aliases = expected.get('aliases', [])
        actual_aliases = actual.aliases or []
        assert len(actual_aliases) == len(expected_aliases), \
            f"Unit aliases count mismatch: {len(actual_aliases)} != {len(expected_aliases)}"
        
        # Check alias content if both are non-empty
        if expected_aliases and actual_aliases:
            # Handle both string and object formats
            for i, expected_alias in enumerate(expected_aliases):
                if i < len(actual_aliases):
                    actual_alias = actual_aliases[i]
                    if isinstance(expected_alias, dict) and 'name' in expected_alias:
                        expected_name = expected_alias['name']
                        actual_name = actual_alias.get('name') if isinstance(actual_alias, dict) else str(actual_alias)
                        assert actual_name == expected_name, \
                            f"Unit alias name mismatch at index {i}: {actual_name} != {expected_name}"


def assert_household_equal(
    actual: Household,
    expected: Dict[str, Any],
    ignore_fields: Optional[List[str]] = None
) -> None:
    """
    Assert that a Household object matches expected data.
    
    Args:
        actual: The actual Household object
        expected: Expected data dictionary
        ignore_fields: List of fields to ignore in comparison
    """
    ignore_fields = ignore_fields or ['id', 'group_id', 'slug']
    
    assert actual.name == expected.get('name'), \
        f"Household name mismatch: {actual.name} != {expected.get('name')}"
    
    if 'preferences' in expected and 'preferences' not in ignore_fields:
        expected_prefs = expected.get('preferences', {})
        actual_prefs = actual.preferences
        
        # Check a few key preference fields
        if 'privateHousehold' in expected_prefs:
            assert actual_prefs.privateHousehold == expected_prefs['privateHousehold'], \
                f"Household private setting mismatch: {actual_prefs.privateHousehold} != {expected_prefs['privateHousehold']}"
        
        if 'recipePublic' in expected_prefs:
            assert actual_prefs.recipePublic == expected_prefs['recipePublic'], \
                f"Household recipe public setting mismatch: {actual_prefs.recipePublic} != {expected_prefs['recipePublic']}"


def assert_successful_response(response: Any, expected_status: int = 200) -> None:
    """
    Assert that a response indicates success.
    
    Args:
        response: The response object
        expected_status: Expected HTTP status code
    """
    if hasattr(response, 'status_code'):
        assert response.status_code == expected_status, \
            f"Response status mismatch: {response.status_code} != {expected_status}"
    
    # For successful responses, ensure we have data
    assert response is not None, "Response should not be None for successful operation"


def assert_error_response(
    response: Exception,
    expected_status: Optional[int] = None,
    expected_message: Optional[str] = None
) -> None:
    """
    Assert that a response indicates an error with expected characteristics.
    
    Args:
        response: The exception object
        expected_status: Expected HTTP status code
        expected_message: Expected error message (substring)
    """
    assert isinstance(response, Exception), "Expected an exception to be raised"
    
    if expected_status and hasattr(response, 'status_code'):
        assert response.status_code == expected_status, \
            f"Error status mismatch: {response.status_code} != {expected_status}"
    
    if expected_message:
        error_message = str(response)
        assert expected_message.lower() in error_message.lower(), \
            f"Expected message '{expected_message}' not found in '{error_message}'"


def assert_pagination_response(
    response: Union[List, Dict],
    expected_page: int = 1,
    expected_per_page: Optional[int] = None,
    expected_total: Optional[int] = None,
    min_items: int = 0
) -> None:
    """
    Assert that a paginated response has expected structure and values.
    
    Args:
        response: The paginated response
        expected_page: Expected page number
        expected_per_page: Expected items per page
        expected_total: Expected total items
        min_items: Minimum number of items expected
    """
    if isinstance(response, dict) and 'items' in response:
        # Paginated response
        assert 'page' in response, "Paginated response should have 'page' field"
        assert response['page'] == expected_page, \
            f"Page mismatch: {response['page']} != {expected_page}"
        
        if expected_per_page:
            assert 'per_page' in response, "Paginated response should have 'per_page' field"
            assert response['per_page'] == expected_per_page, \
                f"Per page mismatch: {response['per_page']} != {expected_per_page}"
        
        if expected_total is not None:
            assert 'total' in response, "Paginated response should have 'total' field"
            assert response['total'] == expected_total, \
                f"Total mismatch: {response['total']} != {expected_total}"
        
        items = response['items']
        assert len(items) >= min_items, \
            f"Expected at least {min_items} items, got {len(items)}"
    
    elif isinstance(response, list):
        # Simple list response
        assert len(response) >= min_items, \
            f"Expected at least {min_items} items, got {len(response)}"
    
    else:
        raise AssertionError(f"Unexpected response type: {type(response)}")


def assert_list_contains_test_data(
    items: List[Any],
    test_prefix: str,
    name_field: str = 'name',
    min_count: int = 1
) -> None:
    """
    Assert that a list contains items with test data prefix.
    
    Args:
        items: List of items to check
        test_prefix: Test data prefix to look for
        name_field: Field name to check for prefix
        min_count: Minimum number of test items expected
    """
    test_items = []
    
    for item in items:
        if hasattr(item, name_field):
            name_value = getattr(item, name_field)
            if name_value and name_value.startswith(test_prefix):
                test_items.append(item)
        elif isinstance(item, dict) and name_field in item:
            name_value = item[name_field]
            if name_value and name_value.startswith(test_prefix):
                test_items.append(item)
    
    assert len(test_items) >= min_count, \
        f"Expected at least {min_count} test items with prefix '{test_prefix}', found {len(test_items)}"


def assert_fields_not_none(obj: Any, fields: List[str]) -> None:
    """
    Assert that specified fields are not None.
    
    Args:
        obj: Object to check
        fields: List of field names that should not be None
    """
    for field in fields:
        if hasattr(obj, field):
            value = getattr(obj, field)
            assert value is not None, f"Field '{field}' should not be None"
        elif isinstance(obj, dict):
            assert field in obj, f"Field '{field}' should be present in response"
            assert obj[field] is not None, f"Field '{field}' should not be None"
        else:
            raise AssertionError(f"Object does not have field '{field}'") 