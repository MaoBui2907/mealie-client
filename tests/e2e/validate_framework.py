#!/usr/bin/env python3
"""
E2E Framework Validation Script

This script validates the E2E testing framework implementation
by checking imports, structure, and basic functionality.
"""

import sys
import traceback
from pathlib import Path


def validate_imports():
    """Validate that all modules can be imported correctly."""
    print("🔍 Validating imports...")
    
    try:
        # Core framework imports
        from tests.e2e import config
        print("  ✅ config module")
        
        from tests.e2e import conftest
        print("  ✅ conftest module")
        
        from tests.e2e import base_test
        print("  ✅ base_test module")
        
        # Utils imports
        from tests.e2e.utils import E2EDataFactory, E2ECleanup
        print("  ✅ utils.data_factory")
        print("  ✅ utils.cleanup")
        
        from tests.e2e.utils import (
            assert_recipe_equal, 
            assert_user_equal,
            assert_successful_response
        )
        print("  ✅ utils.assertions")
        
        # Test suite imports
        import tests.e2e.test_authentication
        print("  ✅ test_authentication")
        
        import tests.e2e.test_client_lifecycle
        print("  ✅ test_client_lifecycle") 
        
        import tests.e2e.test_recipes_crud
        print("  ✅ test_recipes_crud")
        
        import tests.e2e.test_users_crud
        print("  ✅ test_users_crud")
        
        import tests.e2e.test_groups_crud
        print("  ✅ test_groups_crud")
        
        import tests.e2e.test_shopping_lists_crud
        print("  ✅ test_shopping_lists_crud")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Import failed: {e}")
        traceback.print_exc()
        return False


def validate_structure():
    """Validate framework file structure."""
    print("\n🏗️ Validating structure...")
    
    required_files = [
        "tests/e2e/config.py",
        "tests/e2e/conftest.py", 
        "tests/e2e/base_test.py",
        "tests/e2e/utils/__init__.py",
        "tests/e2e/utils/data_factory.py",
        "tests/e2e/utils/cleanup.py",
        "tests/e2e/utils/assertions.py",
        "tests/e2e/test_authentication.py",
        "tests/e2e/test_client_lifecycle.py",
        "tests/e2e/test_recipes_crud.py",
        "tests/e2e/test_users_crud.py",
        "tests/e2e/test_groups_crud.py",
        "tests/e2e/test_shopping_lists_crud.py",
        "tests/e2e/README.md",
        "tests/e2e/IMPLEMENTATION_SUMMARY.md"
    ]
    
    all_exist = True
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ Missing: {file_path}")
            all_exist = False
    
    return all_exist


def validate_configuration():
    """Validate configuration functionality."""
    print("\n⚙️ Validating configuration...")
    
    try:
        from tests.e2e.config import E2EConfig, get_test_config
        
        # Test config creation
        config = E2EConfig.from_env()
        print("  ✅ Config creation from environment")
        
        # Test config validation (should work even without credentials)
        try:
            config.validate()
            print("  ✅ Config validation (with credentials)")
        except ValueError as e:
            print(f"  ⚠️ Config validation failed (expected without credentials): {e}")
        
        # Test auth kwargs
        auth_kwargs = config.get_auth_kwargs()
        print(f"  ✅ Auth kwargs: {list(auth_kwargs.keys())}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Configuration validation failed: {e}")
        return False


def validate_data_factory():
    """Validate data factory functionality."""
    print("\n🏭 Validating data factory...")
    
    try:
        from tests.e2e.utils import E2EDataFactory
        
        factory = E2EDataFactory()
        
        # Test recipe data generation
        recipe_data = factory.generate_test_recipe_data()
        print(f"  ✅ Recipe data: {recipe_data['name']}")
        
        # Test user data generation
        user_data = factory.generate_test_user_data()
        print(f"  ✅ User data: {user_data['username']}")
        
        # Test group data generation
        group_data = factory.generate_test_group_data()
        print(f"  ✅ Group data: {group_data['name']}")
        
        # Test shopping list data generation
        list_data = factory.generate_test_shopping_list_data()
        print(f"  ✅ Shopping list data: {list_data['name']}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Data factory validation failed: {e}")
        return False


def validate_base_test():
    """Validate base test classes."""
    print("\n🧪 Validating base test classes...")
    
    try:
        from tests.e2e.base_test import BaseE2ETest, AsyncBaseE2ETest
        
        # Test base class instantiation
        base_test = BaseE2ETest()
        print("  ✅ BaseE2ETest instantiation")
        
        async_base_test = AsyncBaseE2ETest()
        print("  ✅ AsyncBaseE2ETest instantiation")
        
        # Test resource tracking
        base_test.track_created_resource('recipes', 'test_id')
        assert 'test_id' in base_test.created_resources['recipes']
        print("  ✅ Resource tracking")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Base test validation failed: {e}")
        return False


def main():
    """Run all validations."""
    print("🚀 E2E Testing Framework Validation")
    print("=" * 50)
    
    validations = [
        ("Imports", validate_imports),
        ("Structure", validate_structure), 
        ("Configuration", validate_configuration),
        ("Data Factory", validate_data_factory),
        ("Base Test Classes", validate_base_test)
    ]
    
    results = []
    for name, validator in validations:
        success = validator()
        results.append((name, success))
    
    # Summary
    print("\n📊 Validation Summary")
    print("=" * 50)
    
    passed = 0
    for name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{name:20} {status}")
        if success:
            passed += 1
    
    total = len(results)
    print(f"\nOverall: {passed}/{total} validations passed")
    
    if passed == total:
        print("\n🎉 Framework validation SUCCESSFUL!")
        print("✅ The E2E testing framework is ready for use!")
        return 0
    else:
        print("\n⚠️ Some validations failed.")
        print("❌ Please check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 