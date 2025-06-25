from fastapi_users import FastAPIUsers
from fastapi_users.authentication import (
    AuthenticationBackend,
    CookieTransport,
    JWTStrategy,
)

from src.config import settings
from src.users.UserModel import User

cookie_transport = CookieTransport(
    cookie_name="Cookie_PV_data",
    cookie_secure=False,
    cookie_max_age=1209600,
    cookie_samesite="Lax",
)


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=settings.SECRET_AUTH, lifetime_seconds=1209600)


auth_backend = AuthenticationBackend(
    name="jwt",
    transport=cookie_transport,
    get_strategy=get_jwt_strategy,
)


def get_fastapi_users():
    from src.auth.AuthRepository import get_user_manager

    return FastAPIUsers[User, int](
        get_user_manager,
        [auth_backend],
    )


_fastapi_users = None


def get_fastapi_users_instance():
    global _fastapi_users
    if _fastapi_users is None:
        _fastapi_users = get_fastapi_users()
    return _fastapi_users


fastapi_users_instance = get_fastapi_users_instance()
current_user = fastapi_users_instance.current_user()
