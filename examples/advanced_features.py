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

from mealie_client import MealieClient
from mealie_client.exceptions import MealieAPIError, AuthenticationError, NotFoundError


async def advanced_recipe_operations(client: MealieClient):
    """Demonstrate advanced recipe operations."""
    print("\n🔍 Advanced Recipe Operations")
    print("-" * 30)
    
    # Complex filtering example
    print("Searching with complex filters...")
    
    filtered_recipes = await client.recipes.get_all(
        search="vegetarian quick",
        tags=["vegetarian", "quick"],
        order_by="created_at",
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
        ]
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
    updated_list = await client.shopping_lists.get(shopping_list.id)
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
                "recipe_id": recipe_id
            }
            
            try:
                meal_plan = await client.meal_plans.create(meal_plan_data)
                created_plans.append(meal_plan)
                print(f"  📝 Planned {meal_type} for {plan_date.strftime('%A')}")
            except MealieAPIError as e:
                print(f"  ❌ Failed to create meal plan: {e}")
    
    print(f"✅ Created {len(created_plans)} meal plans for the week")
    return created_plans


async def user_management(client: MealieClient):
    """Demonstrate user management (requires admin privileges)."""
    print("\n👥 User Management")
    print("-" * 30)
    
    try:
        # Get current users
        users = await client.users.get_all()
        print(f"📊 Current users: {len(users)}")
        
        # Note: Groups are read-only via API
        groups = await client.groups.get_all()
        print(f"📊 Current groups: {len(groups)} (read-only via API)")
        
        print("Note: Groups must be created/updated/deleted via Mealie web interface")
        return None
        
    except AuthenticationError:
        print("❌ Admin privileges required for user management")
        return None
    except MealieAPIError as e:
        print(f"❌ User management error: {e}")
        return None


async def error_handling_examples(client: MealieClient):
    """Demonstrate proper error handling patterns."""
    print("\n⚠️  Error Handling Examples")
    print("-" * 30)
    
    # Example 1: Handle not found errors
    try:
        non_existent_recipe = await client.recipes.get("definitely-not-a-recipe")
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
        print("✅ User creation successful")
    except AuthenticationError:
        print("✅ Properly handled AuthenticationError for insufficient privileges")
    except MealieAPIError as e:
        print(f"❌ Unexpected API error: {e}")


async def cleanup_test_data(client: MealieClient, created_recipes, shopping_list, meal_plans):
    """Clean up test data created during the demo."""
    print("\n🧹 Cleaning up test data...")
    print("-" * 30)
    
    # Delete created recipes
    for recipe in created_recipes:
        try:
            await client.recipes.delete(recipe.slug)
            print(f"  ✅ Deleted recipe: {recipe.name}")
        except Exception as e:
            print(f"  ❌ Failed to delete recipe {recipe.name}: {e}")
    
    # Delete shopping list
    if shopping_list:
        try:
            await client.shopping_lists.delete(shopping_list.id)
            print(f"  ✅ Deleted shopping list: {shopping_list.name}")
        except Exception as e:
            print(f"  ❌ Failed to delete shopping list: {e}")
    
    # Delete meal plans
    for plan in meal_plans:
        try:
            await client.meal_plans.delete(plan.id)
            print(f"  ✅ Deleted meal plan: {plan.title}")
        except Exception as e:
            print(f"  ❌ Failed to delete meal plan: {e}")
    
    # Note: Groups cannot be deleted via API - must be done manually via web interface


async def main():
    """Main demo function."""
    print("🚀 Mealie SDK Advanced Features Demo")
    print("=" * 50)
    
    async with MealieClient(
        base_url=os.getenv("MEALIE_BASE_URL", "https://your-mealie-instance.com"),
        api_token=os.getenv("MEALIE_API_TOKEN", "your-api-token")
    ) as client:
        
        try:
            # Run advanced recipe operations
            created_recipes = await advanced_recipe_operations(client)
            
            # Shopping list management
            shopping_list = await shopping_list_management(client)
            
            # Meal planning workflow
            meal_plans = await meal_planning_workflow(client, created_recipes)
            
            # === Groups Management ===
            print("\n--- Groups Management (Read-Only) ---")
            
            # Note: Groups cannot be created, updated, or deleted via API
            # They must be managed through the Mealie web interface
            
            # Get all groups
            print("Getting all groups...")
            groups = await client.groups.get_all()
            print(f"Found {len(groups)} groups")
            
            if groups:
                # Get details of first group
                group = groups[0]
                print(f"Getting details for group: {group.name}")
                detailed_group = await client.groups.get(group.id)
                print(f"Group details - Name: {detailed_group.name}, Users: {detailed_group.get_user_count()}")
            else:
                print("No groups found. Groups must be created via web interface.")
            
            print("Note: Group create/update/delete operations must be done via Mealie web interface")
            
            # Error handling examples
            await error_handling_examples(client)
            
            # Clean up test data
            await cleanup_test_data(client, created_recipes, shopping_list, meal_plans)
            
        except Exception as e:
            print(f"❌ Demo error: {e}")
            print("Make sure your Mealie instance is running and API token is valid")
    
    print("\n🎉 Advanced features demo completed!")


if __name__ == "__main__":
    # Set up environment variables for testing
    print("To run this advanced demo, set the following environment variables:")
    print("  export MEALIE_BASE_URL='https://your-mealie-instance.com'")
    print("  export MEALIE_API_TOKEN='your-api-token'")
    print("Note: Some features require admin privileges")
    print()
    
    # Run the demo
    asyncio.run(main()) 