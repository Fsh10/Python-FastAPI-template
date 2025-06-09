from functools import wraps
from typing import Callable

from src.utils.managers.translations import translations


def translate_error_messages(func: Callable) -> Callable:
    """
    Decorator for automatic translation of error messages
    based on user language.
    """

    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            user = None
            for arg in args:
                if hasattr(arg, "language"):
                    user = arg
                    break

            if not user:
                for value in kwargs.values():
                    if hasattr(value, "language"):
                        user = value
                        break

            if user and hasattr(e, "message"):
                e.message = translations.get_message(e.message, user.language)

            raise e

    return wrapper


def translate_response_messages(func: Callable) -> Callable:
    """
    Decorator for automatic translation of response messages
    based on user language.
    """

    @wraps(func)
    async def wrapper(*args, **kwargs):
        result = await func(*args, **kwargs)

        user = None
        for arg in args:
            if hasattr(arg, "language"):
                user = arg
                break

        if not user:
            for value in kwargs.values():
                if hasattr(value, "language"):
                    user = value
                    break

        if user and isinstance(result, dict) and "message" in result:
            result["message"] = translations.get_message(
                result["message"], user.language
            )

        return result

    return wrapper
