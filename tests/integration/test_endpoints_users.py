"""
Integration tests for users endpoint.

Tests cover user CRUD operations, current user management,
validation scenarios, and user-specific workflows.
"""

import pytest
import httpx

from mealie_client.exceptions import NotFoundError, ValidationError, AuthorizationError, AuthenticationError


class TestUsersCRUD:
    """Test suite for basic user CRUD operations."""

    @pytest.mark.integration
    async def test_get_all_users(self, integration_httpx_mock, authenticated_client, mock_pagination_response):
        """Test fetching all users with pagination."""
        users_response = {
            "items": [
                {
                    "id": f"user_{i}",
                    "username": f"user{i}",
                    "email": f"user{i}@test.com",
                    "full_name": f"Test User {i}",
                    "admin": i == 1,
                    "created_at": "2023-01-01T00:00:00Z"
                }
                for i in range(1, 11)
            ],
            "page": 1,
            "per_page": 10,
            "total": 25
        }
        
        integration_httpx_mock.get("/api/admin/users").mock(
            return_value=httpx.Response(200, json=users_response)
        )
        
        users = await authenticated_client.users.get_all(page=1, per_page=10)
        
        assert len(users) == 10
        assert users[0].username == "user1"
        assert users[0].admin is True
        assert users[1].admin is False

    @pytest.mark.integration
    async def test_get_user_by_id(self, integration_httpx_mock, authenticated_client):
        """Test fetching a specific user by ID."""
        user_id = "test-user-123"
        user_data = {
            "id": user_id,
            "username": "testuser",
            "email": "testuser@example.com",
            "full_name": "Test User",
            "admin": False,
            "group": "default",
            "created_at": "2023-01-01T00:00:00Z",
            "updated_at": "2023-01-01T00:00:00Z"
        }
        
        integration_httpx_mock.get(f"/api/admin/users/{user_id}").mock(
            return_value=httpx.Response(200, json=user_data)
        )
        
        user = await authenticated_client.users.get(user_id)
        
        assert user.id == user_id
        assert user.username == "testuser"
        assert user.email == "testuser@example.com"
        assert user.admin is False

    @pytest.mark.integration
    async def test_get_user_not_found(self, integration_httpx_mock, authenticated_client):
        """Test handling of non-existent user."""
        user_id = "nonexistent-user"
        integration_httpx_mock.get(f"/api/admin/users/{user_id}").mock(
            return_value=httpx.Response(404, json={"detail": "User not found"})
        )
        
        with pytest.raises(NotFoundError) as exc_info:
            await authenticated_client.users.get(user_id)
        
        assert exc_info.value.status_code == 404
        assert exc_info.value.resource_type == "user"
        assert exc_info.value.resource_id == user_id

    @pytest.mark.integration
    async def test_create_user_success(self, integration_httpx_mock, authenticated_client):
        """Test successful user creation."""
        user_data = {
            "username": "newuser",
            "email": "newuser@example.com", 
            "full_name": "New User",
            "password": "secure_password_123",
            "admin": False
        }
        
        created_user = {
            "id": "new-user-456",
            **user_data,
            "created_at": "2023-01-01T00:00:00Z"
        }
        del created_user["password"]  # Password not returned
        
        integration_httpx_mock.post("/api/admin/users").mock(
            return_value=httpx.Response(201, json=created_user)
        )
        
        user = await authenticated_client.users.create(user_data)
        
        assert user.id == "new-user-456"
        assert user.username == "newuser"
        assert user.email == "newuser@example.com"

    @pytest.mark.integration
    async def test_create_user_validation_error(self, integration_httpx_mock, authenticated_client):
        """Test user creation with validation errors."""
        integration_httpx_mock.post("/api/admin/users").mock(
            return_value=httpx.Response(422, json={
                "detail": [
                    {"loc": ["email"], "msg": "invalid email format", "type": "value_error.email"},
                    {"loc": ["username"], "msg": "field required", "type": "value_error.missing"}
                ]
            })
        )
        
        with pytest.raises(ValidationError) as exc_info:
            await authenticated_client.users.create({"email": "invalid-email"})
        
        assert exc_info.value.status_code == 422
        assert "invalid email format" in str(exc_info.value)

    @pytest.mark.integration
    async def test_update_user_success(self, integration_httpx_mock, authenticated_client):
        """Test successful user update."""
        user_id = "update-user-789"
        update_data = {
            "full_name": "Updated User Name",
            "email": "updated@example.com"
        }
        
        updated_user = {
            "id": user_id,
            "username": "testuser",
            **update_data,
            "admin": False,
            "updated_at": "2023-01-01T12:00:00Z"
        }
        
        integration_httpx_mock.put(f"/api/admin/users/{user_id}").mock(
            return_value=httpx.Response(200, json=updated_user)
        )
        
        user = await authenticated_client.users.update(user_id, update_data)
        
        assert user.id == user_id
        assert user.full_name == "Updated User Name"
        assert user.email == "updated@example.com"

    @pytest.mark.integration
    async def test_delete_user_success(self, integration_httpx_mock, authenticated_client):
        """Test successful user deletion."""
        user_id = "delete-user-101"
        integration_httpx_mock.delete(f"/api/admin/users/{user_id}").mock(
            return_value=httpx.Response(204)
        )
        
        result = await authenticated_client.users.delete(user_id)
        assert result is True

    @pytest.mark.integration
    async def test_delete_user_not_found(self, integration_httpx_mock, authenticated_client):
        """Test deletion of non-existent user."""
        user_id = "nonexistent-user"
        integration_httpx_mock.delete(f"/api/admin/users/{user_id}").mock(
            return_value=httpx.Response(404, json={"detail": "User not found"})
        )
        
        with pytest.raises(NotFoundError):
            await authenticated_client.users.delete(user_id)


class TestCurrentUser:
    """Test suite for current user operations."""

    @pytest.mark.integration
    async def test_get_current_user(self, integration_httpx_mock, authenticated_client):
        """Test fetching current authenticated user."""
        current_user_data = {
            "id": "current-user-123",
            "username": "currentuser",
            "email": "current@example.com",
            "full_name": "Current User",
            "admin": True,
            "group": "admins",
            "created_at": "2023-01-01T00:00:00Z"
        }
        
        integration_httpx_mock.get("/api/users/self").mock(
            return_value=httpx.Response(200, json=current_user_data)
        )
        
        user = await authenticated_client.users.get_self()
        
        assert user.id == "current-user-123"
        assert user.username == "currentuser"
        assert user.admin is True

    @pytest.mark.integration
    async def test_get_current_user_unauthenticated(self, integration_httpx_mock, authenticated_client):
        """Test getting current user when not authenticated."""
        integration_httpx_mock.get("/api/users/self").mock(
            return_value=httpx.Response(401, json={"detail": "Not authenticated"})
        )
        
        with pytest.raises(AuthenticationError): # 401 status should raise AuthenticationError
            await authenticated_client.users.get_self()


class TestUserValidation:
    """Test suite for user input validation scenarios."""

    @pytest.mark.integration
    async def test_create_user_duplicate_username(self, integration_httpx_mock, authenticated_client):
        """Test creating user with duplicate username."""
        integration_httpx_mock.post("/api/admin/users").mock(
            return_value=httpx.Response(409, json={
                "detail": "Username already exists"
            })
        )
        
        user_data = {
            "username": "existinguser",
            "email": "new@example.com",
            "password": "password123"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            await authenticated_client.users.create(user_data)
        
        assert exc_info.value.status_code == 409

    @pytest.mark.integration
    async def test_create_user_duplicate_email(self, integration_httpx_mock, authenticated_client):
        """Test creating user with duplicate email."""
        integration_httpx_mock.post("/api/admin/users").mock(
            return_value=httpx.Response(409, json={
                "detail": "Email already exists"
            })
        )
        
        user_data = {
            "username": "newuser",
            "email": "existing@example.com",
            "password": "password123"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            await authenticated_client.users.create(user_data)
        
        assert exc_info.value.status_code == 409

    @pytest.mark.integration
    async def test_create_user_weak_password(self, integration_httpx_mock, authenticated_client):
        """Test creating user with weak password."""
        integration_httpx_mock.post("/api/admin/users").mock(
            return_value=httpx.Response(422, json={
                "detail": [
                    {"loc": ["password"], "msg": "password too short", "type": "value_error"}
                ]
            })
        )
        
        user_data = {
            "username": "newuser",
            "email": "new@example.com",
            "password": "123"  # Too short
        }
        
        with pytest.raises(ValidationError):
            await authenticated_client.users.create(user_data)

    @pytest.mark.integration
    async def test_update_user_invalid_email(self, integration_httpx_mock, authenticated_client):
        """Test updating user with invalid email format."""
        user_id = "test-user"
        integration_httpx_mock.put(f"/api/admin/users/{user_id}").mock(
            return_value=httpx.Response(422, json={
                "detail": [
                    {"loc": ["email"], "msg": "invalid email format", "type": "value_error.email"}
                ]
            })
        )
        
        with pytest.raises(ValidationError):
            await authenticated_client.users.update(user_id, {"email": "invalid-email"})


class TestUserPermissions:
    """Test suite for user permission and authorization scenarios."""

    @pytest.mark.integration
    async def test_non_admin_cannot_create_user(self, integration_httpx_mock, authenticated_client):
        """Test that non-admin users cannot create users."""
        integration_httpx_mock.post("/api/admin/users").mock(
            return_value=httpx.Response(403, json={
                "detail": "Insufficient permissions to create users"
            })
        )
        
        user_data = {
            "username": "newuser",
            "email": "new@example.com",
            "password": "password123"
        }
        
        with pytest.raises(AuthorizationError) as exc_info:
            await authenticated_client.users.create(user_data)
        
        assert exc_info.value.status_code == 403

    @pytest.mark.integration
    async def test_non_admin_cannot_delete_user(self, integration_httpx_mock, authenticated_client):
        """Test that non-admin users cannot delete users."""
        user_id = "some-user"
        integration_httpx_mock.delete(f"/api/admin/users/{user_id}").mock(
            return_value=httpx.Response(403, json={
                "detail": "Insufficient permissions to delete users"
            })
        )
        
        with pytest.raises(AuthorizationError):
            await authenticated_client.users.delete(user_id)

    @pytest.mark.integration
    async def test_user_cannot_modify_admin_status(self, integration_httpx_mock, authenticated_client):
        """Test that regular users cannot modify admin status."""
        user_id = "test-user"
        integration_httpx_mock.put(f"/api/admin/users/{user_id}").mock(
            return_value=httpx.Response(403, json={
                "detail": "Cannot modify admin status"
            })
        )
        
        with pytest.raises(AuthorizationError):
            await authenticated_client.users.update(user_id, {"admin": True})


class TestUserPagination:
    """Test suite for user pagination and filtering."""

    @pytest.mark.integration
    async def test_get_users_with_pagination(self, integration_httpx_mock, authenticated_client):
        """Test user pagination with different page sizes."""
        page2_response = {
            "items": [
                {
                    "id": f"user_{i}",
                    "username": f"user{i}",
                    "email": f"user{i}@test.com"
                }
                for i in range(21, 31)  # Page 2 users
            ],
            "page": 2,
            "per_page": 10,
            "total": 45
        }
        
        integration_httpx_mock.get("/api/admin/users").mock(
            return_value=httpx.Response(200, json=page2_response)
        )
        
        users = await authenticated_client.users.get_all(page=2, per_page=10)
        
        assert len(users) == 10
        assert users[0].username == "user21"

    @pytest.mark.integration
    async def test_get_users_empty_page(self, integration_httpx_mock, authenticated_client):
        """Test requesting page beyond available data."""
        empty_response = {
            "items": [],
            "page": 10,
            "per_page": 10,
            "total": 25
        }
        
        integration_httpx_mock.get("/api/admin/users").mock(
            return_value=httpx.Response(200, json=empty_response)
        )
        
        users = await authenticated_client.users.get_all(page=10, per_page=10)
        assert len(users) == 0

    @pytest.mark.integration
    async def test_batch_user_operations(self, integration_httpx_mock, authenticated_client):
        """Test creating multiple users in sequence."""
        users_to_create = [
            {"username": f"batch_user_{i}", "email": f"batch{i}@test.com", "password": "password123"}
            for i in range(1, 4)
        ]
        
        created_users = []
        for i, user_data in enumerate(users_to_create, 1):
            created_user = {
                "id": f"batch-user-{i}",
                **user_data,
                "admin": False,
                "created_at": "2023-01-01T00:00:00Z"
            }
            del created_user["password"]
            created_users.append(created_user)
            
            integration_httpx_mock.post("/api/admin/users").mock(
                return_value=httpx.Response(201, json=created_user)
            )
        
        # Create users in batch
        results = []
        for user_data in users_to_create:
            user = await authenticated_client.users.create(user_data)
            results.append(user)
        
        assert len(results) == 3
        assert all(user.username.startswith("batch_user_") for user in results) 