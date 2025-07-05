"""
Unit tests for UsersManager endpoint.

Tests cover user-related operations including CRUD operations,
user management, and authentication flows.
"""

from datetime import UTC
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from mealie_client.endpoints.users import UsersManager
from mealie_client.models.user import User, UserCreateRequest, UserUpdateRequest, UserSummary
from mealie_client.exceptions import NotFoundError


class TestUsersManagerInit:
    """Test suite for UsersManager initialization."""

    @pytest.mark.unit
    def test_init(self, mealie_client):
        """Test UsersManager initialization."""
        users_manager = UsersManager(mealie_client)
        assert users_manager.client == mealie_client


class TestUsersManagerGetAll:
    """Test suite for get_all method."""

    @pytest.fixture
    def users_manager(self, mealie_client):
        """Create a UsersManager for testing."""
        return UsersManager(mealie_client)

    @pytest.mark.unit
    async def test_get_all_default_params(self, users_manager, mock_users_list_response):
        """Test get_all with default parameters."""
        users_manager.client.get = AsyncMock(return_value=mock_users_list_response)
        
        result = await users_manager.get_all()
        
        # Verify request was made with correct parameters
        users_manager.client.get.assert_called_once()
        call_args = users_manager.client.get.call_args
        assert call_args[0][0] == "admin/users"
        
        # Verify default pagination parameters
        params = call_args[1]["params"]
        assert params["page"] == 1
        assert params["perPage"] == 50
        
        # Verify response handling
        assert len(result) == 2
        assert all(isinstance(user, UserSummary) for user in result)

    @pytest.mark.unit
    async def test_get_all_with_pagination(self, users_manager, mock_users_list_response):
        """Test get_all with custom pagination parameters."""
        users_manager.client.get = AsyncMock(return_value=mock_users_list_response)
        
        await users_manager.get_all(page=3, per_page=25)
        users_manager.client.get.assert_called_once_with("admin/users", params={'page': 3, 'perPage': 25, 'orderByNullPosition': 'last'})

    @pytest.mark.unit
    async def test_get_all_handles_simple_list_response(self, users_manager):
        """Test get_all handles response that's a simple list."""
        simple_list_response = [create_test_user_data() for _ in range(3)]
        users_manager.client.get = AsyncMock(return_value=simple_list_response)
        
        result = await users_manager.get_all()
        
        assert len(result) == 3
        assert all(isinstance(user, UserSummary) for user in result)

    @pytest.mark.unit
    async def test_get_all_handles_empty_response(self, users_manager):
        """Test get_all handles empty response."""
        users_manager.client.get = AsyncMock(return_value={"items": []})
        
        result = await users_manager.get_all()
        
        assert result == []


class TestUsersManagerGet:
    """Test suite for get method."""

    @pytest.fixture
    def users_manager(self, mealie_client):
        return UsersManager(mealie_client)

    @pytest.mark.unit
    async def test_get_by_id_success(self, users_manager):
        """Test successful get by user ID."""
        user_data = create_test_user_data()
        users_manager.client.get = AsyncMock(return_value=user_data)
        
        result = await users_manager.get("user-123")
        
        users_manager.client.get.assert_called_once_with("admin/users/user-123")
        assert isinstance(result, User)
        assert result.id == user_data["id"]

    @pytest.mark.unit
    async def test_get_not_found_raises_error(self, users_manager):
        """Test that get raises NotFoundError for 404 responses."""
        mock_exception = Exception("Not found")
        mock_exception.status_code = 404
        users_manager.client.get = AsyncMock(side_effect=mock_exception)
        
        with pytest.raises(NotFoundError) as exc_info:
            await users_manager.get("nonexistent-user")
        
        assert exc_info.value.resource_type == "user"
        assert exc_info.value.resource_id == "nonexistent-user"

    @pytest.mark.unit
    async def test_get_other_errors_passthrough(self, users_manager):
        """Test that non-404 errors are passed through."""
        mock_exception = Exception("Server error")
        mock_exception.status_code = 500
        users_manager.client.get = AsyncMock(side_effect=mock_exception)
        
        with pytest.raises(Exception) as exc_info:
            await users_manager.get("user-123")
        
        assert exc_info.value.status_code == 500


class TestUsersManagerCreate:
    """Test suite for create method."""

    @pytest.fixture
    def users_manager(self, mealie_client):
        return UsersManager(mealie_client)

    @pytest.mark.unit
    async def test_create_with_request_object(self, users_manager):
        """Test create with UserCreateRequest object."""
        request_data = UserCreateRequest(
            username="newuser",
            email="newuser@example.com",
            full_name="New User",
            password="password123",
            admin=False
        )
        response_data = create_test_user_data(
            username="newuser",
            email="newuser@example.com",
            full_name="New User"
        )
        users_manager.client.post = AsyncMock(return_value=response_data)
        
        result = await users_manager.create(request_data)
        
        users_manager.client.post.assert_called_once()
        call_args = users_manager.client.post.call_args
        assert call_args[0][0] == "admin/users"
        assert "json_data" in call_args[1]
        
        json_data = call_args[1]["json_data"]
        assert json_data["username"] == "newuser"
        assert json_data["email"] == "newuser@example.com"
        assert json_data["password"] == "password123"
        
        assert isinstance(result, User)
        assert result.username == "newuser"

    @pytest.mark.unit
    async def test_create_with_dict(self, users_manager):
        """Test create with dictionary data."""
        request_data = {
            "username": "dictuser",
            "email": "dict@example.com",
            "full_name": "Dict User",
            "password": "dictpass",
            "admin": True
        }
        response_data = create_test_user_data(username="dictuser", admin=True)
        users_manager.client.post = AsyncMock(return_value=response_data)
        
        result = await users_manager.create(request_data)
        
        call_args = users_manager.client.post.call_args
        json_data = call_args[1]["json_data"]
        assert json_data["admin"] is True
        
        assert isinstance(result, User)
        assert result.username == "dictuser"

    @pytest.mark.unit
    async def test_create_handles_validation_error(self, users_manager):
        """Test create handles validation errors appropriately."""
        from mealie_client.exceptions import ValidationError
        
        request_data = UserCreateRequest(
            username="",  # Invalid: empty username
            email="invalid-email",  # Invalid email format
            password="123"  # Too short password
        )
        
        mock_exception = ValidationError(
            "Validation failed",
            validation_errors={
                "username": ["Username cannot be empty"],
                "email": ["Invalid email format"],
                "password": ["Password too short"]
            }
        )
        users_manager.client.post = AsyncMock(side_effect=mock_exception)
        
        with pytest.raises(ValidationError) as exc_info:
            await users_manager.create(request_data)
        
        assert "Validation failed" in str(exc_info.value)


class TestUsersManagerUpdate:
    """Test suite for update method."""

    @pytest.fixture
    def users_manager(self, mealie_client):
        return UsersManager(mealie_client)

    @pytest.mark.unit
    async def test_update_success(self, users_manager):
        """Test successful user update."""
        update_data = {
            "full_name": "Updated User Name",
            "email": "updated@example.com",
            "admin": True
        }
        response_data = create_test_user_data(
            full_name="Updated User Name",
            email="updated@example.com",
            admin=True
        )
        users_manager.client.put = AsyncMock(return_value=response_data)
        
        result = await users_manager.update("user-123", update_data)
        
        users_manager.client.put.assert_called_once()
        call_args = users_manager.client.put.call_args
        assert call_args[0][0] == "admin/users/user-123"
        
        json_data = call_args[1]["json_data"]
        assert json_data["full_name"] == "Updated User Name"
        assert json_data["admin"] is True
        
        assert isinstance(result, User)
        assert result.full_name == "Updated User Name"

    @pytest.mark.unit
    async def test_update_with_request_object(self, users_manager):
        """Test update with UserUpdateRequest object."""
        update_request = UserUpdateRequest(
            full_name="Request Updated",
            admin=False
        )
        response_data = create_test_user_data(full_name="Request Updated", admin=False)
        users_manager.client.put = AsyncMock(return_value=response_data)
        
        result = await users_manager.update("user-123", update_request)
        
        assert isinstance(result, User)
        assert result.full_name == "Request Updated"

    @pytest.mark.unit
    async def test_update_not_found_raises_error(self, users_manager):
        """Test that update raises NotFoundError for nonexistent user."""
        mock_exception = Exception("Not found")
        mock_exception.status_code = 404
        users_manager.client.put = AsyncMock(side_effect=mock_exception)
        
        with pytest.raises(NotFoundError) as exc_info:
            await users_manager.update("nonexistent", {"full_name": "Updated"})
        
        assert exc_info.value.resource_type == "user"
        assert exc_info.value.resource_id == "nonexistent"

    @pytest.mark.unit
    async def test_update_partial_data(self, users_manager):
        """Test updating user with partial data."""
        update_data = {"admin": True}  # Only update admin status
        response_data = create_test_user_data(admin=True)
        users_manager.client.put = AsyncMock(return_value=response_data)
        
        result = await users_manager.update("user-123", update_data)
        
        call_args = users_manager.client.put.call_args
        json_data = call_args[1]["json_data"]
        assert json_data == {"admin": True}  # Only admin field updated
        
        assert result.admin is True


class TestUsersManagerDelete:
    """Test suite for delete method."""

    @pytest.fixture
    def users_manager(self, mealie_client):
        return UsersManager(mealie_client)

    @pytest.mark.unit
    async def test_delete_success(self, users_manager):
        """Test successful user deletion."""
        users_manager.client.delete = AsyncMock(return_value=None)
        
        result = await users_manager.delete("user-123")
        
        users_manager.client.delete.assert_called_once_with("admin/users/user-123")
        assert result is True

    @pytest.mark.unit
    async def test_delete_not_found_raises_error(self, users_manager):
        """Test that delete raises NotFoundError for nonexistent user."""
        mock_exception = Exception("Not found")
        mock_exception.status_code = 404
        users_manager.client.delete = AsyncMock(side_effect=mock_exception)
        
        with pytest.raises(NotFoundError) as exc_info:
            await users_manager.delete("nonexistent")
        
        assert exc_info.value.resource_type == "user"
        assert exc_info.value.resource_id == "nonexistent"

    @pytest.mark.unit
    async def test_delete_admin_user_may_have_restrictions(self, users_manager):
        """Test that deleting admin user may have special restrictions."""
        # This test simulates a scenario where the API prevents deletion of admin users
        from mealie_client.exceptions import AuthorizationError
        
        mock_exception = AuthorizationError("Cannot delete admin user")
        mock_exception.status_code = 403
        users_manager.client.delete = AsyncMock(side_effect=mock_exception)
        
        with pytest.raises(AuthorizationError) as exc_info:
            await users_manager.delete("admin-user-123")
        
        assert "Cannot delete admin user" in str(exc_info.value)


class TestUsersManagerGetCurrent:
    """Test suite for get_current method."""

    @pytest.fixture
    def users_manager(self, mealie_client):
        return UsersManager(mealie_client)

    @pytest.mark.unit
    async def test_get_current_success(self, users_manager):
        """Test successful get current user."""
        current_user_data = create_test_user_data(
            username="current_user",
            email="current@example.com",
            admin=True
        )
        users_manager.client.get = AsyncMock(return_value=current_user_data)
        
        result = await users_manager.get_self()
        
        users_manager.client.get.assert_called_once_with("users/self", params={'page': 1, 'perPage': 50, 'orderByNullPosition': 'last'})
        assert isinstance(result, User)
        assert result.username == "current_user"
        assert result.admin is True

    @pytest.mark.unit
    async def test_get_current_unauthenticated_raises_error(self, users_manager):
        """Test that get_current raises error when not authenticated."""
        from mealie_client.exceptions import AuthenticationError
        
        mock_exception = AuthenticationError("Not authenticated")
        mock_exception.status_code = 401
        users_manager.client.get = AsyncMock(side_effect=mock_exception)
        
        with pytest.raises(AuthenticationError) as exc_info:
            await users_manager.get_self()
        
        assert exc_info.value.status_code == 401


class TestUsersManagerAdvancedOperations:
    """Test suite for advanced user operations."""

    @pytest.fixture
    def users_manager(self, mealie_client):
        return UsersManager(mealie_client)

    @pytest.mark.unit
    async def test_create_admin_user(self, users_manager):
        """Test creating an admin user."""
        admin_request = UserCreateRequest(
            username="admin",
            email="admin@example.com",
            full_name="Administrator",
            password="secure_admin_password",
            admin=True
        )
        response_data = create_test_user_data(
            username="admin",
            admin=True,
            full_name="Administrator"
        )
        users_manager.client.post = AsyncMock(return_value=response_data)
        
        result = await users_manager.create(admin_request)
        
        call_args = users_manager.client.post.call_args
        json_data = call_args[1]["json_data"]
        assert json_data["admin"] is True
        
        assert result.admin is True
        assert result.username == "admin"

    @pytest.mark.unit
    async def test_demote_admin_user(self, users_manager):
        """Test demoting an admin user to regular user."""
        update_data = {"admin": False}
        response_data = create_test_user_data(admin=False)
        users_manager.client.put = AsyncMock(return_value=response_data)
        
        result = await users_manager.update("admin-user-123", update_data)
        
        assert result.admin is False

    @pytest.mark.unit
    async def test_update_user_permissions(self, users_manager):
        """Test updating user permissions."""
        permissions_update = {
            "can_invite": True,
            "can_manage": True,
            "can_organize": False,
            "advanced": True
        }
        response_data = create_test_user_data(**permissions_update)
        users_manager.client.put = AsyncMock(return_value=response_data)
        
        result = await users_manager.update("user-123", permissions_update)
        
        call_args = users_manager.client.put.call_args
        json_data = call_args[1]["json_data"]
        assert json_data["can_invite"] is True
        assert json_data["can_manage"] is True
        assert json_data["can_organize"] is False
        assert json_data["advanced"] is True

    @pytest.mark.unit
    async def test_bulk_user_operations_pattern(self, users_manager):
        """Test pattern for bulk user operations (if implemented)."""
        # This test demonstrates how bulk operations might work
        user_ids = ["user-1", "user-2", "user-3"]
        
        # Simulate getting multiple users
        users_data = [create_test_user_data(id=user_id) for user_id in user_ids]
        
        # In a real implementation, this might be a single API call
        # For now, simulate multiple individual calls
        users_manager.client.get = AsyncMock(side_effect=users_data)
        
        results = []
        for user_id in user_ids:
            user = await users_manager.get(user_id)
            results.append(user)
        
        assert len(results) == 3
        assert all(isinstance(user, User) for user in results)


class TestUsersManagerErrorHandling:
    """Test suite for error handling scenarios."""

    @pytest.fixture
    def users_manager(self, mealie_client):
        return UsersManager(mealie_client)

    @pytest.mark.unit
    async def test_create_duplicate_username_error(self, users_manager):
        """Test handling of duplicate username creation."""
        from mealie_client.exceptions import ValidationError
        
        request_data = UserCreateRequest(
            username="existing_user",
            email="new@example.com",
            password="password123"
        )
        
        mock_exception = ValidationError(
            "Username already exists",
            validation_errors={"username": ["This username is already taken"]}
        )
        users_manager.client.post = AsyncMock(side_effect=mock_exception)
        
        with pytest.raises(ValidationError) as exc_info:
            await users_manager.create(request_data)
        
        assert "username" in exc_info.value.validation_errors

    @pytest.mark.unit
    async def test_create_duplicate_email_error(self, users_manager):
        """Test handling of duplicate email creation."""
        from mealie_client.exceptions import ValidationError
        
        request_data = UserCreateRequest(
            username="newuser",
            email="existing@example.com",
            password="password123"
        )
        
        mock_exception = ValidationError(
            "Email already exists",
            validation_errors={"email": ["This email is already registered"]}
        )
        users_manager.client.post = AsyncMock(side_effect=mock_exception)
        
        with pytest.raises(ValidationError) as exc_info:
            await users_manager.create(request_data)
        
        assert "email" in exc_info.value.validation_errors

    @pytest.mark.unit
    async def test_insufficient_permissions_error(self, users_manager):
        """Test handling of insufficient permissions for user operations."""
        from mealie_client.exceptions import AuthorizationError
        
        mock_exception = AuthorizationError("Insufficient permissions for user management")
        mock_exception.status_code = 403
        users_manager.client.post = AsyncMock(side_effect=mock_exception)
        
        request_data = UserCreateRequest(
            username="newuser",
            email="new@example.com",
            password="password123",
            admin=True  # Trying to create admin user without permission
        )
        
        with pytest.raises(AuthorizationError) as exc_info:
            await users_manager.create(request_data)
        
        assert exc_info.value.status_code == 403


# Helper function for creating test user data
def create_test_user_data(**kwargs):
    """Create test user data for testing."""
    from datetime import datetime
    
    defaults = {
        "id": str(uuid4()),
        "username": f"user_{uuid4().hex[:8]}",
        "email": f"test_{uuid4().hex[:8]}@example.com",
        "full_name": "Test User",
        "admin": False,
        "group": "default-group",
        "advanced": False,
        "can_invite": False,
        "can_manage": False,
        "can_organize": False,
        "login_attemps": 0,
        "locked_at": None,
        "date_updated": datetime.now(UTC).isoformat(),
        "cache_key": str(uuid4())
    }
    defaults.update(kwargs)
    return defaults 