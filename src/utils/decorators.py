from functools import wraps
from typing import Any, Callable

from src.exceptions import PermissionDeniedException
from src.users.UserModel import User


def protect(role_id: int = 1):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            from src.users.UserService import get_current_user

            user = await get_current_user()
            if role_id != user.role_id:
                raise PermissionDeniedException()
            return await func(*args, **kwargs)

        return wrapper

    return decorator


async def protect_route(user: User, role_id: int = 1):
    if user.role_id != role_id:
        raise PermissionDeniedException()


def logged(func: Callable) -> Callable:
    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        return await func(*args, **kwargs)

    return wrapper


def catch_error(func: Callable) -> Callable:
    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            from loguru import logger

            logger.error(f"Error in {func.__name__}: {str(e)}")
            raise

    return wrapper
