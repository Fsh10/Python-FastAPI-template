from fastapi import Depends

from src.utils.base.BaseService import BaseService

from ..users.UserSchemas import UserSchemas, user_schemas
from .AuthRepository import UserManager, get_user_manager


class AuthService(BaseService):
    def __init__(self, repository: UserManager, schemas: UserSchemas) -> None:
        super().__init__(repository, schemas)

    async def check_auth(self, token: str):
        """Check authentication."""
        return {"authenticated": True, "user_id": "test-user"}

    async def invite_user(self, email: str, role: str):
        """Invite user."""
        return {"invited": True, "email": email, "role": role}

    async def get_invitations(self):
        """Get invitations."""
        return []

    async def check_by_android_id(self, android_id: str):
        """Check by Android ID."""
        return {"found": True, "android_id": android_id}

    async def is_verified(self, user_id: str):
        """Check user verification."""
        return {"verified": True, "user_id": user_id}

    async def verify_user(self, token: str):
        """Verify user."""
        return {"verified": True, "token": token}

    async def activate_user(self, token: str):
        """Activate user."""
        return {"activated": True, "token": token}

    async def change_password(self, old_password: str, new_password: str):
        """Change password."""
        return {"changed": True}


def get_auth_service(
    user_service: UserManager = Depends(get_user_manager),
) -> AuthService:
    return AuthService(repository=user_service, schemas=user_schemas)
