"""
Basic usage example for the Mealie SDK.

This example demonstrates how to perform common operations like:
- Connecting to a Mealie instance
- Retrieving recipes
- Creating new recipes
- Managing meal plans
"""

import asyncio
import os
from datetime import date, timedelta

from mealie_sdk import MealieClient


async def main():
    """Main example function."""
    # Initialize the client using environment variables or direct parameters
    client = MealieClient(
        base_url=os.getenv("MEALIE_BASE_URL", "https://your-mealie-instance.com"),
        api_token=os.getenv("MEALIE_API_TOKEN", "your-api-token")
    )
    
    print("🍽️  Mealie SDK Basic Usage Example")
    print("=" * 40)
    
    try:
        # Get all recipes
        print("\n📖 Fetching all recipes...")
        recipes = await client.recipes.get_all(per_page=5)
        print(f"Found {len(recipes)} recipes (showing first 5)")
        
        for recipe in recipes[:3]:  # Show first 3
            print(f"  - {recipe.name}")
        
        # Get a specific recipe by slug if recipes exist
        if recipes:
            first_recipe = recipes[0]
            print(f"\n🔍 Getting detailed info for: {first_recipe.name}")
            detailed_recipe = await client.recipes.get_by_slug(first_recipe.slug)
            if detailed_recipe:
                print(f"  Description: {detailed_recipe.description or 'No description'}")
                print(f"  Prep time: {detailed_recipe.prep_time or 'Not specified'}")
                print(f"  Cook time: {detailed_recipe.cook_time or 'Not specified'}")
        
        # Search recipes with filters
        print("\n🔎 Searching for vegetarian recipes...")
        vegetarian_recipes = await client.recipes.get_all(
            query_filter='tags.name CONTAINS "vegetarian"',
            per_page=3
        )
        print(f"Found {len(vegetarian_recipes)} vegetarian recipes")
        
        # Create a new recipe example
        print("\n✨ Creating a new example recipe...")
        new_recipe_data = {
            "name": "SDK Test Recipe",
            "description": "A test recipe created via the Mealie SDK",
            "recipe_ingredient": [
                {"note": "2 cups all-purpose flour"},
                {"note": "1 cup granulated sugar"},
                {"note": "1/2 cup butter, softened"},
                {"note": "2 large eggs"},
                {"note": "1 tsp vanilla extract"}
            ],
            "recipe_instructions": [
                {"text": "Preheat oven to 350°F (175°C)"},
                {"text": "Mix flour and sugar in a large bowl"},
                {"text": "Add butter, eggs, and vanilla extract"},
                {"text": "Mix until well combined"},
                {"text": "Bake for 25-30 minutes until golden brown"}
            ],
            "prep_time": "PT15M",  # 15 minutes in ISO 8601 duration format
            "cook_time": "PT30M",  # 30 minutes
            "recipe_yield": "12 servings",
            "tags": [{"name": "dessert"}, {"name": "baking"}]
        }
        
        created_recipe = await client.recipes.create(new_recipe_data)
        print(f"✅ Created recipe: {created_recipe.name}")
        print(f"   Slug: {created_recipe.slug}")
        
        # Get current meal plans
        print("\n📅 Checking current meal plans...")
        today = date.today()
        meal_plans = await client.meal_plans.get_all(
            start_date=today,
            end_date=today + timedelta(days=7)
        )
        print(f"Found {len(meal_plans)} meal plans for this week")
        
        # Create a meal plan example
        print("\n📋 Creating a sample meal plan...")
        meal_plan_data = {
            "date": today.isoformat(),
            "entry_type": "dinner",
            "title": "Test Dinner Plan",
            "recipe_id": created_recipe.id if created_recipe else None
        }
        
        if created_recipe:
            meal_plan = await client.meal_plans.create(meal_plan_data)
            print(f"✅ Created meal plan for {meal_plan.date}")
        
        # Clean up - delete the test recipe
        if created_recipe:
            print(f"\n🧹 Cleaning up - deleting test recipe...")
            await client.recipes.delete(created_recipe.slug)
            print("✅ Test recipe deleted")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Make sure your Mealie instance is running and API token is valid")
    
    finally:
        # Close the client connection
        await client.close()
    
    print("\n🎉 Example completed!")


if __name__ == "__main__":
    # Set up environment variables for testing
    print("To run this example, set the following environment variables:")
    print("  export MEALIE_BASE_URL='https://your-mealie-instance.com'")
    print("  export MEALIE_API_TOKEN='your-api-token'")
    print()
    
    # Run the example
    asyncio.run(main()) 