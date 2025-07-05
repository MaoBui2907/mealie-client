"""
E2E Users CRUD Tests

This module tests complete CRUD operations for users including
creation, reading, updating, deletion, and user management features.
"""

import pytest
from mealie_client.exceptions import NotFoundError
from mealie_client.models import UserSummary
from mealie_client.models.user import UserCreateRequest



class TestE2EUsersCRUD:
    """Test full CRUD operations for users."""

    @pytest.mark.asyncio
    async def test_users_crud_full(self, e2e_test_base, sample_user_data):
        users = await e2e_test_base.client.users.get_all()
        assert len(users) > 0
        assert all(isinstance(user, UserSummary) for user in users)

        user = await e2e_test_base.client.users.create(UserCreateRequest(**sample_user_data))
        assert user is not None
        assert user.username == sample_user_data["username"]
        assert user.email == sample_user_data["email"]
        assert user.id is not None

        all_users = await e2e_test_base.client.users.get_all()
        assert len(all_users) > 0
        assert user.id in [user.id for user in all_users]
        

        self_user = await e2e_test_base.client.users.get_self()
        assert self_user is not None
        assert self_user.id is not None
        assert self_user.admin is True

        await e2e_test_base.client.users.delete(user.id)
        with pytest.raises(NotFoundError):
            await e2e_test_base.client.users.get(user.id)       
        
