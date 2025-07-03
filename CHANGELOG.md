# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial project setup
- Basic SDK structure
- Comprehensive documentation

## [0.1.0] - 2025-01-07

### Added
- Initial release of Mealie SDK
- Async HTTP client using httpx
- Pydantic models for type safety
- Support for Recipe management (CRUD operations)
- Support for Meal Plan management
- Support for Shopping List management
- Support for User and Group management
- Authentication via API tokens
- Advanced filtering and pagination support
- Comprehensive error handling
- Example scripts for basic and advanced usage
- GitHub Actions CI/CD pipeline
- Full test suite setup
- Professional documentation
- PDM project management setup

### Features
- **Recipe Management**: Full CRUD operations for recipes
- **Meal Planning**: Create and manage meal plans
- **Shopping Lists**: Manage shopping lists and items
- **User Management**: Handle users and groups (admin privileges required)
- **Authentication**: Secure token-based authentication
- **Filtering**: Advanced query capabilities with pagination
- **File Operations**: Support for uploading recipe images
- **Type Safety**: Full type hints and Pydantic validation
- **Async Support**: Modern async/await patterns
- **Error Handling**: Comprehensive custom exceptions

### Technical
- Python 3.8+ support
- PDM for dependency management
- Ruff for linting and formatting
- MyPy for static type checking
- Pytest for testing
- MkDocs for documentation
- GitHub Actions for CI/CD
- Pre-commit hooks for code quality

[unreleased]: https://github.com/yourusername/mealie-sdk/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/yourusername/mealie-sdk/releases/tag/v0.1.0 