"""
E2E Testing Configuration

This module manages configuration for end-to-end testing including
environment setup, server configuration, and test data management.
"""

import os
from typing import Optional, Dict, Any
from dataclasses import dataclass


@dataclass
class E2EConfig:
    """Configuration for E2E testing."""
    
    # Server Configuration
    base_url: str
    timeout: float = 30.0
    max_retries: int = 3
    retry_delay: float = 2.0
    
    # Authentication
    username: Optional[str] = None
    password: Optional[str] = None
    api_token: Optional[str] = None
    
    # Test Settings
    cleanup_data: bool = True
    run_performance_tests: bool = False
    run_load_tests: bool = False
    parallel_workers: int = 1
    
    # Test Data Prefixes (for easy cleanup)
    test_prefix: str = "e2e_test_"
    test_user_prefix: str = "e2e_user_"
    test_recipe_prefix: str = "e2e_recipe_"
    test_group_prefix: str = "e2e_group_"
    
    @classmethod
    def from_env(cls) -> "E2EConfig":
        """Create configuration from environment variables."""
        return cls(
            # Required
            base_url=os.getenv("E2E_MEALIE_BASE_URL", "https://demo.mealie.io"),
            
            # Authentication - prioritize API token
            api_token=os.getenv("E2E_MEALIE_API_TOKEN"),
            username=os.getenv("E2E_MEALIE_USERNAME"),
            password=os.getenv("E2E_MEALIE_PASSWORD"),
            
            # Server settings
            timeout=float(os.getenv("E2E_TIMEOUT", "30.0")),
            max_retries=int(os.getenv("E2E_MAX_RETRIES", "3")),
            retry_delay=float(os.getenv("E2E_RETRY_DELAY", "2.0")),
            
            # Test settings
            cleanup_data=os.getenv("E2E_CLEANUP_DATA", "true").lower() == "true",
            run_performance_tests=os.getenv("E2E_RUN_PERFORMANCE", "false").lower() == "true",
            run_load_tests=os.getenv("E2E_RUN_LOAD", "false").lower() == "true",
            parallel_workers=int(os.getenv("E2E_PARALLEL_WORKERS", "1")),
            
            # Test data prefixes
            test_prefix=os.getenv("E2E_TEST_PREFIX", "e2e_test_"),
            test_user_prefix=os.getenv("E2E_USER_PREFIX", "e2e_user_"),
            test_recipe_prefix=os.getenv("E2E_RECIPE_PREFIX", "e2e_recipe_"),
            test_group_prefix=os.getenv("E2E_GROUP_PREFIX", "e2e_group_"),
        )
    
    def validate(self) -> None:
        """Validate configuration."""
        if not self.base_url:
            raise ValueError("E2E_MEALIE_BASE_URL is required")
        
        if not self.api_token and not (self.username and self.password):
            raise ValueError(
                "Either E2E_MEALIE_API_TOKEN or both E2E_MEALIE_USERNAME "
                "and E2E_MEALIE_PASSWORD must be provided"
            )
    
    def get_auth_kwargs(self) -> Dict[str, Any]:
        """Get authentication kwargs for MealieClient."""
        if self.api_token:
            return {"api_token": self.api_token}
        else:
            return {"username": self.username, "password": self.password}


# Global configuration instance
config = E2EConfig.from_env()


def get_test_config() -> E2EConfig:
    """Get the current test configuration."""
    return config


def is_performance_enabled() -> bool:
    """Check if performance tests are enabled."""
    return config.run_performance_tests


def is_load_testing_enabled() -> bool:
    """Check if load tests are enabled."""
    return config.run_load_tests


def should_cleanup_data() -> bool:
    """Check if test data should be cleaned up."""
    return config.cleanup_data 