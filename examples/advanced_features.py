"""
Advanced features example for the Mealie SDK.

This example demonstrates advanced functionality like:
- Complex recipe filtering and searching
- Batch operations
- Shopping list management
- User and group management (requires admin privileges)
- File uploads and downloads
- Error handling patterns
"""

import asyncio
import os
from datetime import date, timedelta
from pathlib import Path

from mealie_sdk import MealieClient
from mealie_sdk.exceptions import MealieAPIError, AuthenticationError, NotFoundError


async def advanced_recipe_operations(client: MealieClient):
    """Demonstrate advanced recipe operations."""
    print("\n🔍 Advanced Recipe Operations")
    print("-" * 30)
    
    # Complex filtering example
    print("Searching with complex filters...")
    complex_filter = (
        '(tags.name CONTAINS "vegetarian" OR tags.name CONTAINS "vegan") '
        'AND cook_time <= "PT45M" '
        'AND created_at >= "2023-01-01"'
    )
    
    filtered_recipes = await client.recipes.get_all(
        query_filter=complex_filter,
        order_by="created_at,cook_time",
        order_direction="desc",
        per_page=10
    )
    print(f"Found {len(filtered_recipes)} recipes matching complex criteria")
    
    # Batch recipe creation
    print("\nCreating multiple recipes in batch...")
    batch_recipes = [
        {
            "name": f"Batch Recipe {i}",
            "description": f"Recipe {i} created in batch",
            "recipe_ingredient": [{"note": f"Ingredient {j}"} for j in range(1, 4)],
            "recipe_instructions": [{"text": f"Step {j}"} for j in range(1, 3)],
            "tags": [{"name": "batch-created"}]
        }
        for i in range(1, 4)
    ]
    
    created_recipes = []
    for recipe_data in batch_recipes:
        try:
            recipe = await client.recipes.create(recipe_data)
            created_recipes.append(recipe)
            print(f"  ✅ Created: {recipe.name}")
        except MealieAPIError as e:
            print(f"  ❌ Failed to create recipe: {e}")
    
    return created_recipes


async def shopping_list_management(client: MealieClient):
    """Demonstrate shopping list management."""
    print("\n🛒 Shopping List Management")
    print("-" * 30)
    
    # Create a comprehensive shopping list
    shopping_list_data = {
        "name": "Weekly Grocery List",
        "list_items": [
            {"note": "2 lbs organic chicken breast", "checked": False},
            {"note": "1 dozen free-range eggs", "checked": False},
            {"note": "2 cups basmati rice", "checked": False},
            {"note": "Fresh vegetables for salad", "checked": False},
            {"note": "Olive oil - extra virgin", "checked": False}
        ],
        "extras": {
            "store_preference": "Whole Foods",
            "budget_limit": "150.00",
            "priority": "high"
        }
    }
    
    shopping_list = await client.shopping_lists.create(shopping_list_data)
    print(f"✅ Created shopping list: {shopping_list.name}")
    
    # Add more items dynamically
    additional_items = [
        {"note": "Greek yogurt - plain", "checked": False},
        {"note": "Seasonal fruit selection", "checked": False}
    ]
    
    for item_data in additional_items:
        await client.shopping_lists.add_item(shopping_list.id, item_data)
        print(f"  ➕ Added item: {item_data['note']}")
    
    # Retrieve and update the shopping list
    updated_list = await client.shopping_lists.get_by_id(shopping_list.id)
    print(f"📋 Shopping list now has {len(updated_list.list_items)} items")
    
    return shopping_list


async def meal_planning_workflow(client: MealieClient, recipes):
    """Demonstrate comprehensive meal planning."""
    print("\n📅 Meal Planning Workflow")
    print("-" * 30)
    
    # Create meal plans for the week
    today = date.today()
    meal_types = ["breakfast", "lunch", "dinner"]
    
    created_plans = []
    for i in range(7):  # One week
        plan_date = today + timedelta(days=i)
        for meal_type in meal_types:
            # Use a random recipe if available
            recipe_id = recipes[i % len(recipes)].id if recipes else None
            
            meal_plan_data = {
                "date": plan_date.isoformat(),
                "entry_type": meal_type,
                "title": f"{meal_type.title()} for {plan_date.strftime('%A')}",
                "recipe_id": recipe_id,
                "extras": {
                    "meal_prep_day": "Sunday",
                    "dietary_notes": "Family friendly"
                }
            }
            
            try:
                meal_plan = await client.meal_plans.create(meal_plan_data)
                created_plans.append(meal_plan)
                print(f"  📝 Planned {meal_type} for {plan_date.strftime('%A')}")
            except MealieAPIError as e:
                print(f"  ❌ Failed to create meal plan: {e}")
    
    print(f"✅ Created {len(created_plans)} meal plans for the week")
    return created_plans


async def user_group_management(client: MealieClient):
    """Demonstrate user and group management (requires admin privileges)."""
    print("\n👥 User & Group Management")
    print("-" * 30)
    
    try:
        # Get current users
        users = await client.users.get_all()
        print(f"📊 Current users: {len(users)}")
        
        # Get groups
        groups = await client.groups.get_all()
        print(f"📊 Current groups: {len(groups)}")
        
        # Create a new group
        group_data = {
            "name": "SDK Test Group",
            "description": "A test group created via SDK"
        }
        
        new_group = await client.groups.create(group_data)
        print(f"✅ Created group: {new_group.name}")
        
        return new_group
        
    except AuthenticationError:
        print("❌ Admin privileges required for user/group management")
        return None
    except MealieAPIError as e:
        print(f"❌ Group management error: {e}")
        return None


async def error_handling_examples(client: MealieClient):
    """Demonstrate proper error handling patterns."""
    print("\n⚠️  Error Handling Examples")
    print("-" * 30)
    
    # Example 1: Handle not found errors
    try:
        non_existent_recipe = await client.recipes.get_by_slug("definitely-not-a-recipe")
    except NotFoundError:
        print("✅ Properly handled NotFoundError for non-existent recipe")
    except MealieAPIError as e:
        print(f"❌ Unexpected API error: {e}")
    
    # Example 2: Handle authentication errors
    try:
        # This would fail if we don't have admin privileges
        await client.users.create({
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpass"
        })
    except AuthenticationError:
        print("✅ Properly handled AuthenticationError for insufficient privileges")
    except MealieAPIError as e:
        print(f"❌ Unexpected API error: {e}")
    
    # Example 3: Handle validation errors
    try:
        # Invalid recipe data
        await client.recipes.create({
            "name": "",  # Empty name should cause validation error
            "description": "Invalid recipe"
        })
    except MealieAPIError as e:
        print(f"✅ Properly handled validation error: {e}")


async def cleanup_test_data(client: MealieClient, created_recipes, shopping_list, meal_plans, group):
    """Clean up test data created during the example."""
    print("\n🧹 Cleaning Up Test Data")
    print("-" * 30)
    
    # Delete created recipes
    for recipe in created_recipes:
        try:
            await client.recipes.delete(recipe.slug)
            print(f"  🗑️  Deleted recipe: {recipe.name}")
        except Exception as e:
            print(f"  ❌ Failed to delete recipe {recipe.name}: {e}")
    
    # Delete shopping list
    if shopping_list:
        try:
            await client.shopping_lists.delete(shopping_list.id)
            print(f"  🗑️  Deleted shopping list: {shopping_list.name}")
        except Exception as e:
            print(f"  ❌ Failed to delete shopping list: {e}")
    
    # Delete meal plans
    for plan in meal_plans:
        try:
            await client.meal_plans.delete(plan.id)
            print(f"  🗑️  Deleted meal plan for {plan.date}")
        except Exception as e:
            print(f"  ❌ Failed to delete meal plan: {e}")
    
    # Delete group
    if group:
        try:
            await client.groups.delete(group.id)
            print(f"  🗑️  Deleted group: {group.name}")
        except Exception as e:
            print(f"  ❌ Failed to delete group: {e}")


async def main():
    """Main advanced example function."""
    print("🚀 Mealie SDK Advanced Features Example")
    print("=" * 45)
    
    # Initialize client
    client = MealieClient(
        base_url=os.getenv("MEALIE_BASE_URL", "https://your-mealie-instance.com"),
        api_token=os.getenv("MEALIE_API_TOKEN", "your-api-token")
    )
    
    # Track created items for cleanup
    created_recipes = []
    shopping_list = None
    meal_plans = []
    group = None
    
    try:
        # Advanced recipe operations
        created_recipes = await advanced_recipe_operations(client)
        
        # Shopping list management
        shopping_list = await shopping_list_management(client)
        
        # Meal planning workflow
        if created_recipes:
            meal_plans = await meal_planning_workflow(client, created_recipes)
        
        # User and group management (optional - requires admin)
        group = await user_group_management(client)
        
        # Error handling examples
        await error_handling_examples(client)
        
    except Exception as e:
        print(f"❌ Unexpected error during example: {e}")
    
    finally:
        # Clean up test data
        await cleanup_test_data(client, created_recipes, shopping_list, meal_plans, group)
        
        # Close client connection
        await client.close()
    
    print("\n🎉 Advanced example completed!")


if __name__ == "__main__":
    print("To run this advanced example, set the following environment variables:")
    print("  export MEALIE_BASE_URL='https://your-mealie-instance.com'")
    print("  export MEALIE_API_TOKEN='your-api-token'")
    print("\nNote: Some features require admin privileges on your Mealie instance.")
    print()
    
    asyncio.run(main()) 