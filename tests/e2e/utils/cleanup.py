"""
E2E Test Data Cleanup

This module provides utilities for cleaning up test data created during
end-to-end testing to ensure a clean state between test runs.
"""

import asyncio
from typing import List, Optional, Dict, Any
from mealie_client import MealieClient
from mealie_client.exceptions import NotFoundError, MealieAPIError
from ..config import get_test_config


class E2ECleanup:
    """Handles cleanup of E2E test data."""
    
    def __init__(self, client: MealieClient):
        """Initialize cleanup with MealieClient."""
        self.client = client
        self.config = get_test_config()
        
    async def cleanup_all_test_data(self) -> Dict[str, int]:
        """
        Clean up all test data created during E2E testing.
        
        Returns:
            Dictionary with cleanup counts for each resource type
        """
        results = {}
        
        # Run cleanups in sequence to avoid conflicts
        results['recipes'] = await self.cleanup_test_recipes()
        results['users'] = await self.cleanup_test_users()
        results['groups'] = await self.cleanup_test_groups()
        results['meal_plans'] = await self.cleanup_test_meal_plans()
        results['shopping_lists'] = await self.cleanup_test_shopping_lists()
        
        return results
    
    async def cleanup_test_recipes(self) -> int:
        """
        Clean up test recipes.
        
        Returns:
            Number of recipes cleaned up
        """
        if not self.client.recipes:
            return 0
            
        cleanup_count = 0
        
        try:
            # Get all recipes and filter for test recipes
            recipes = await self.client.recipes.get_all(per_page=100)
            
            for recipe in recipes:
                if (recipe.name and recipe.name.startswith(self.config.test_recipe_prefix)) or \
                   (recipe.slug and recipe.slug.startswith(self.config.test_recipe_prefix)):
                    try:
                        await self.client.recipes.delete(recipe.id or recipe.slug)
                        cleanup_count += 1
                        print(f"Cleaned up test recipe: {recipe.name}")
                    except (NotFoundError, MealieAPIError) as e:
                        print(f"Failed to cleanup recipe {recipe.name}: {e}")
                        
        except Exception as e:
            print(f"Error during recipe cleanup: {e}")
            
        return cleanup_count
    
    async def cleanup_test_users(self) -> int:
        """
        Clean up test users.
        
        Returns:
            Number of users cleaned up
        """
        if not self.client.users:
            return 0
            
        cleanup_count = 0
        
        try:
            # Get all users and filter for test users
            users = await self.client.users.get_all(per_page=100)
            
            for user in users:
                if user.username and user.username.startswith(self.config.test_user_prefix):
                    try:
                        await self.client.users.delete(user.id)
                        cleanup_count += 1
                        print(f"Cleaned up test user: {user.username}")
                    except (NotFoundError, MealieAPIError) as e:
                        print(f"Failed to cleanup user {user.username}: {e}")
                        
        except Exception as e:
            print(f"Error during user cleanup: {e}")
            
        return cleanup_count
    
    async def cleanup_test_groups(self) -> int:
        """
        Clean up test groups.
        
        Note: Groups cannot be deleted via Mealie API and must be deleted manually
        through the web interface. This method only reports groups that need cleanup.
        
        Returns:
            Number of groups that need manual cleanup (always 0 since we can't auto-delete)
        """
        if not self.client.groups:
            return 0
            
        cleanup_count = 0
        groups_needing_cleanup = []
        
        try:
            # Get all groups and filter for test groups
            groups = await self.client.groups.get_all()
            
            for group in groups:
                if group.name and group.name.startswith(self.config.test_group_prefix):
                    groups_needing_cleanup.append(group)
                        
        except Exception as e:
            print(f"Error during group cleanup scan: {e}")
            
        if groups_needing_cleanup:
            print(f"\n⚠️  Manual cleanup required for {len(groups_needing_cleanup)} test groups:")
            for group in groups_needing_cleanup:
                print(f"  - Group '{group.name}' (ID: {group.id}) - Delete manually via web interface")
            print("  Note: Groups must be deleted manually through the Mealie web interface")
            print("  as the API does not support group deletion.\n")
            
        return 0  # Always 0 since we can't auto-delete groups
    
    async def cleanup_test_meal_plans(self) -> int:
        """
        Clean up test meal plans.
        
        Returns:
            Number of meal plans cleaned up
        """
        if not self.client.meal_plans:
            return 0
            
        cleanup_count = 0
        
        try:
            # Get all meal plans and filter for test meal plans
            meal_plans = await self.client.meal_plans.get_all()
            
            for plan in meal_plans:
                if plan.title and plan.title.startswith(self.config.test_prefix):
                    try:
                        await self.client.meal_plans.delete(plan.id)
                        cleanup_count += 1
                        print(f"Cleaned up test meal plan: {plan.title}")
                    except (NotFoundError, MealieAPIError) as e:
                        print(f"Failed to cleanup meal plan {plan.title}: {e}")
                        
        except Exception as e:
            print(f"Error during meal plan cleanup: {e}")
            
        return cleanup_count
    
    async def cleanup_test_shopping_lists(self) -> int:
        """
        Clean up test shopping lists.
        
        Returns:
            Number of shopping lists cleaned up
        """
        if not self.client.shopping_lists:
            return 0
            
        cleanup_count = 0
        
        try:
            # Get all shopping lists and filter for test lists
            shopping_lists = await self.client.shopping_lists.get_all()
            
            for shopping_list in shopping_lists:
                if shopping_list.name and shopping_list.name.startswith(self.config.test_prefix):
                    try:
                        await self.client.shopping_lists.delete(shopping_list.id)
                        cleanup_count += 1
                        print(f"Cleaned up test shopping list: {shopping_list.name}")
                    except (NotFoundError, MealieAPIError) as e:
                        print(f"Failed to cleanup shopping list {shopping_list.name}: {e}")
                        
        except Exception as e:
            print(f"Error during shopping list cleanup: {e}")
            
        return cleanup_count
    
    async def cleanup_specific_resources(
        self,
        recipe_ids: Optional[List[str]] = None,
        user_ids: Optional[List[str]] = None,
        group_ids: Optional[List[str]] = None,
        meal_plan_ids: Optional[List[str]] = None,
        shopping_list_ids: Optional[List[str]] = None,
    ) -> Dict[str, int]:
        """
        Clean up specific resources by ID.
        
        Args:
            recipe_ids: List of recipe IDs to delete
            user_ids: List of user IDs to delete
            group_ids: List of group IDs to delete
            meal_plan_ids: List of meal plan IDs to delete
            shopping_list_ids: List of shopping list IDs to delete
            
        Returns:
            Dictionary with cleanup counts for each resource type
        """
        results = {'recipes': 0, 'users': 0, 'groups': 0, 'meal_plans': 0, 'shopping_lists': 0}
        
        # Clean up recipes
        if recipe_ids and self.client.recipes:
            for recipe_id in recipe_ids:
                try:
                    await self.client.recipes.delete(recipe_id)
                    results['recipes'] += 1
                except (NotFoundError, MealieAPIError):
                    pass
        
        # Clean up users
        if user_ids and self.client.users:
            for user_id in user_ids:
                try:
                    await self.client.users.delete(user_id)
                    results['users'] += 1
                except (NotFoundError, MealieAPIError):
                    pass
        
        # Clean up groups - Note: Groups cannot be deleted via API
        if group_ids and self.client.groups:
            print(f"\n⚠️  Manual cleanup required for {len(group_ids)} groups:")
            for group_id in group_ids:
                try:
                    group = await self.client.groups.get(group_id) 
                    print(f"  - Group '{group.name}' (ID: {group_id}) - Delete manually via web interface")
                except (NotFoundError, MealieAPIError):
                    print(f"  - Group ID: {group_id} - Group not found or already deleted")
            print("  Note: Groups must be deleted manually through the Mealie web interface")
            print("  as the API does not support group deletion.\n")
            # results['groups'] remains 0 since we can't auto-delete
        
        # Clean up meal plans
        if meal_plan_ids and self.client.meal_plans:
            for plan_id in meal_plan_ids:
                try:
                    await self.client.meal_plans.delete(plan_id)
                    results['meal_plans'] += 1
                except (NotFoundError, MealieAPIError):
                    pass
        
        # Clean up shopping lists
        if shopping_list_ids and self.client.shopping_lists:
            for list_id in shopping_list_ids:
                try:
                    await self.client.shopping_lists.delete(list_id)
                    results['shopping_lists'] += 1
                except (NotFoundError, MealieAPIError):
                    pass
        
        return results


# Convenience functions
async def cleanup_test_data(client: MealieClient) -> Dict[str, int]:
    """Convenience function for cleaning up all test data."""
    cleanup_manager = E2ECleanup(client)
    return await cleanup_manager.cleanup_all_test_data()


async def cleanup_test_recipes(client: MealieClient) -> int:
    """Convenience function for cleaning up test recipes."""
    cleanup_manager = E2ECleanup(client)
    return await cleanup_manager.cleanup_test_recipes()


async def cleanup_test_users(client: MealieClient) -> int:
    """Convenience function for cleaning up test users."""
    cleanup_manager = E2ECleanup(client)
    return await cleanup_manager.cleanup_test_users() 