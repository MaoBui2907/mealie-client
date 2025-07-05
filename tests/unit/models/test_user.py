"""
Unit tests for user models.

Tests cover User model, request/response models, and user-related
data structures with validation and role management.
"""

from datetime import datetime

import pytest

from mealie_client.models.user import (
    User,
    UserCreateRequest,
    UserUpdateRequest,
    UserSummary,
    UserFilter,
)


class TestUser:
    """Test suite for User model."""

    @pytest.mark.unit
    def test_init_with_defaults(self):
        """Test User initialization with default values."""
        user = User()
        
        assert user.id is None
        assert user.username == ""
        assert user.email == ""
        assert user.full_name is None
        assert user.admin is False
        assert user.group is None
        assert user.advanced is False

    @pytest.mark.unit
    def test_init_with_basic_fields(self):
        """Test User initialization with basic fields."""
        user = User(
            id="user-123",
            username="testuser",
            email="test@example.com",
            full_name="Test User"
        )
        
        assert user.id == "user-123"
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.full_name == "Test User"

    @pytest.mark.unit
    def test_init_with_admin_user(self):
        """Test User initialization as admin."""
        user = User(
            username="admin",
            email="admin@example.com",
            admin=True,
            can_invite=True,
            can_manage=True,
            can_organize=True,
            advanced=True
        )
        
        assert user.username == "admin"
        assert user.admin is True
        assert user.can_invite is True
        assert user.can_manage is True
        assert user.can_organize is True
        assert user.advanced is True

    @pytest.mark.unit
    def test_init_with_group_info(self):
        """Test User initialization with group information."""
        user = User(
            username="groupuser",
            email="group@example.com",
            group="Family Kitchen",
            group_id="group-456"
        )
        
        assert user.username == "groupuser"
        assert user.group == "Family Kitchen"

    @pytest.mark.unit
    def test_init_with_favorite_recipes(self):
        """Test User initialization with favorite recipes."""
        favorites = ["recipe-1", "recipe-2", "recipe-3"]
        user = User(
            username="foodlover",
            email="lover@example.com",
            favorite_recipes=favorites
        )
        
        assert user.username == "foodlover"

    @pytest.mark.unit
    def test_init_with_auth_info(self):
        """Test User initialization with authentication info."""
        user = User(
            username="authuser",
            email="auth@example.com",
            auth_method="LDAP",
            login_attemps=2
        )
        
        assert user.username == "authuser"

    @pytest.mark.unit
    def test_init_with_datetime_strings(self):
        """Test User initialization with datetime strings."""
        user = User(
            username="dateduser",
            email="dated@example.com",
            password_reset_time="2023-12-25T14:30:45",
            locked_at="2023-12-26T10:15:30",
            created_at="2023-12-20T09:00:00",
            updated_at="2023-12-27T16:45:00"
        )
        
        assert user.username == "dateduser"
    
    @pytest.mark.unit
    def test_to_dict_serialization(self):
        """Test User to_dict serialization."""
        user = User(
            username="serialize",
            email="serialize@example.com",
            admin=True,
            created_at=datetime(2023, 12, 25, 14, 30, 45)
        )
        
        result = user.to_dict()
        
        assert result["username"] == "serialize"
        assert result["email"] == "serialize@example.com"
        assert result["admin"] is True
        assert result["created_at"] == "2023-12-25T14:30:45"

    @pytest.mark.unit
    def test_from_dict_creation(self):
        """Test User from_dict creation."""
        data = {
            "id": "user-789",
            "username": "fromdict",
            "email": "fromdict@example.com",
            "full_name": "From Dict User",
            "admin": True,
            "favorite_recipes": ["recipe-1", "recipe-2"],
            "created_at": "2023-12-25T14:30:45"
        }
        
        user = User.from_dict(data)
        
        assert isinstance(user, User)
        assert user.id == "user-789"
        assert user.username == "fromdict"
        assert user.email == "fromdict@example.com"
        assert user.full_name == "From Dict User"
        assert user.admin is True


class TestUserCreateRequest:
    """Test suite for UserCreateRequest model."""

    @pytest.mark.unit
    def test_init_with_required_fields(self):
        """Test UserCreateRequest initialization with required fields."""
        request = UserCreateRequest(
            username="newuser",
            email="new@example.com",
            password="securepassword"
        )
        
        assert request.username == "newuser"
        assert request.email == "new@example.com"
        assert request.password == "securepassword"
        assert request.full_name is None
        assert request.admin is False
        assert request.group is None

    @pytest.mark.unit
    def test_init_with_all_fields(self):
        """Test UserCreateRequest initialization with all fields."""
        request = UserCreateRequest(
            username="completeuser",
            email="complete@example.com",
            password="password123",
            full_name="Complete User",
            admin=True,
            group="Test Group"
        )
        
        assert request.username == "completeuser"
        assert request.email == "complete@example.com"
        assert request.password == "password123"
        assert request.full_name == "Complete User"
        assert request.admin is True
        assert request.group == "Test Group"

    @pytest.mark.unit
    def test_to_dict(self):
        """Test UserCreateRequest to_dict conversion."""
        request = UserCreateRequest(
            username="dictuser",
            email="dict@example.com",
            password="dictpass",
            full_name="Dict User"
        )
        result = request.to_dict()
        
        expected = {
            "username": "dictuser",
            "email": "dict@example.com",
            "password": "dictpass",
            "fullName": "Dict User",
            "admin": False,
            "group": None,
            "household": None,
        }
        assert result == expected

    @pytest.mark.unit
    def test_from_dict(self):
        """Test UserCreateRequest from_dict creation."""
        data = {
            "username": "createfromdict",
            "email": "createdict@example.com",
            "password": "createpass",
            "admin": True
        }
        request = UserCreateRequest.from_dict(data)
        
        assert isinstance(request, UserCreateRequest)
        assert request.username == "createfromdict"
        assert request.email == "createdict@example.com"
        assert request.password == "createpass"
        assert request.admin is True


class TestUserUpdateRequest:
    """Test suite for UserUpdateRequest model."""

    @pytest.mark.unit
    def test_init_with_defaults(self):
        """Test UserUpdateRequest initialization with defaults."""
        request = UserUpdateRequest()
        
        assert request.username is None
        assert request.email is None
        assert request.full_name is None
        assert request.admin is None
        assert request.group is None

    @pytest.mark.unit
    def test_init_with_partial_fields(self):
        """Test UserUpdateRequest initialization with partial fields."""
        request = UserUpdateRequest(
            username="updateduser",
            email="updated@example.com"
        )
        
        assert request.username == "updateduser"
        assert request.email == "updated@example.com"
        assert request.full_name is None
        assert request.admin is None

    @pytest.mark.unit
    def test_init_with_all_fields(self):
        """Test UserUpdateRequest initialization with all fields."""
        request = UserUpdateRequest(
            username="allupdated",
            email="allupdate@example.com",
            full_name="All Updated User",
            admin=True,
            group="Updated Group",
            can_invite=True,
            can_manage=True,
            can_organize=True,
            advanced=True
        )
        
        assert request.username == "allupdated"
        assert request.email == "allupdate@example.com"
        assert request.full_name == "All Updated User"
        assert request.admin is True
        assert request.group == "Updated Group"

    @pytest.mark.unit
    def test_partial_updates(self):
        """Test UserUpdateRequest supports partial updates."""
        # Test updating only username
        request1 = UserUpdateRequest(username="newname")
        assert request1.username == "newname"
        assert request1.email is None
        
        # Test updating only permissions
        request2 = UserUpdateRequest(can_invite=True, can_manage=False)
        assert request2.username is None

    @pytest.mark.unit
    def test_to_dict_filters_none_values(self):
        """Test UserUpdateRequest to_dict filters None values."""
        request = UserUpdateRequest(
            username="filtertest",
            email=None,
            admin=True
        )
        result = request.to_dict()
        
        # Should include non-None values
        assert result["username"] == "filtertest"
        assert result["admin"] is True
        # Should include None values as well for complete representation
        assert result["email"] is None


class TestUserSummary:
    """Test suite for UserSummary model."""

    @pytest.mark.unit
    def test_init_with_defaults(self):
        """Test UserSummary initialization with defaults."""
        summary = UserSummary()
        
        assert summary.id is None
        assert summary.username == ""
        assert summary.email == ""
        assert summary.full_name is None
        assert summary.admin is False
        assert summary.group is None

    @pytest.mark.unit
    def test_init_with_fields(self):
        """Test UserSummary initialization with fields."""
        summary = UserSummary(
            id="summary-123",
            username="summaryuser",
            email="summary@example.com",
            full_name="Summary User",
            admin=True,
            group="Summary Group",
            created_at="2023-12-25T14:30:45"
        )
        
        assert summary.id == "summary-123"
        assert summary.username == "summaryuser"
        assert summary.email == "summary@example.com"
        assert summary.full_name == "Summary User"
        assert summary.admin is True
        assert summary.group == "Summary Group"


    @pytest.mark.unit
    def test_from_dict(self):
        """Test UserSummary from_dict creation."""
        data = {
            "id": "fromdict-summary",
            "username": "dictuser",
            "email": "dictuser@example.com",
            "admin": False,
            "created_at": "2023-12-25T14:30:45"
        }
        summary = UserSummary.from_dict(data)
        
        assert isinstance(summary, UserSummary)
        assert summary.id == "fromdict-summary"
        assert summary.username == "dictuser"
        assert summary.admin is False


class TestUserFilter:
    """Test suite for UserFilter model."""

    @pytest.mark.unit
    def test_init_with_defaults(self):
        """Test UserFilter initialization with defaults."""
        filter_obj = UserFilter()
        
        assert filter_obj.page == 1
        assert filter_obj.per_page == 50
        assert filter_obj.order_by is None
        assert filter_obj.order_direction == "asc"
        assert filter_obj.search is None

    @pytest.mark.unit
    def test_init_with_custom_values(self):
        """Test UserFilter initialization with custom values."""
        filter_obj = UserFilter(
            page=2,
            per_page=25,
            order_by="username",
            search="john",
        )
        
        assert filter_obj.page == 2
        assert filter_obj.per_page == 25
        assert filter_obj.order_by == "username"
        assert filter_obj.search == "john"

    # TODO: Implement this test
    @pytest.mark.skip(reason="TODO: Implement this test")
    def test_to_params(self):
        """Test UserFilter to_params conversion."""
        filter_obj = UserFilter(
            page=3,
            per_page=20,
            order_by="email",
            search="test",
        )
        
        params = filter_obj.to_params()
        
        expected = {
            "page": 3,
            "per_page": 20,
            "order_by": "email",
            "order_direction": "asc",
            "search": "test",
        }
        
        # Should include all non-None values
        for key, value in expected.items():
            assert params[key] == value

    @pytest.mark.unit
    def test_to_params_filters_none_values(self):
        """Test UserFilter to_params filters None values."""
        filter_obj = UserFilter(
            page=1,
            search="test",
        )
        params = filter_obj.to_params()
        
        assert params["page"] == 1
        assert params["search"] == "test"

    @pytest.mark.unit
    def test_inherits_from_base_filter(self):
        """Test that UserFilter has base filtering functionality."""
        filter_obj = UserFilter(page=5, search="admin")
        
        # Should have pagination fields
        assert hasattr(filter_obj, 'page')
        assert hasattr(filter_obj, 'per_page')
        assert hasattr(filter_obj, 'order_by')
        assert hasattr(filter_obj, 'order_direction')
        assert filter_obj.page == 5