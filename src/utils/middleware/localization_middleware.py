from typing import Any, Dict

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from src.utils.managers.translations import translations


class LocalizationMiddleware(BaseHTTPMiddleware):
    """Middleware for automatic API response localization."""

    async def dispatch(self, request: Request, call_next):
        """Process request and set user language from headers."""
        language = request.headers.get("Accept-Language", "en")
        if "," in language:
            language = language.split(",")[0].strip()

        language = language[:2]

        if language not in ["en", "zh", "es", "fr", "de", "ja", "ko", "ar", "hi"]:
            language = "en"

        request.state.language = language

        response = await call_next(request)

        return response


def get_user_language(request: Request) -> str:
    """Get user language from request."""
    return getattr(request.state, "language", "en")


def translate_api_response(
    response_data: Dict[str, Any], language: str = "en"
) -> Dict[str, Any]:
    """Translate messages in API response."""
    if not isinstance(response_data, dict):
        return response_data

    translated_data = response_data.copy()

    if "message" in translated_data:
        translated_data["message"] = translations.get_message(
            translated_data["message"], language
        )

    if "detail" in translated_data:
        if isinstance(translated_data["detail"], str):
            translated_data["detail"] = translations.get_message(
                translated_data["detail"], language
            )
        elif isinstance(translated_data["detail"], list):
            translated_data["detail"] = [
                translations.get_message(detail, language)
                if isinstance(detail, str)
                else detail
                for detail in translated_data["detail"]
            ]

    return translated_data
