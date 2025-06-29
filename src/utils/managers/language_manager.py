from enum import Enum
from typing import Dict, List, Optional


class Language(str, Enum):
    """Supported languages."""

    RUSSIAN = "ru"
    ENGLISH = "en"
    CHINESE = "zh"
    SPANISH = "es"
    FRENCH = "fr"
    GERMAN = "de"
    JAPANESE = "ja"
    KOREAN = "ko"
    ARABIC = "ar"
    HINDI = "hi"


class LanguageManager:
    """Manager for working with languages."""

    # List of supported languages
    SUPPORTED_LANGUAGES = {
        Language.RUSSIAN: {"name": "Русский", "native_name": "Русский", "flag": "🇷🇺"},
        Language.ENGLISH: {"name": "English", "native_name": "English", "flag": "🇺🇸"},
        Language.CHINESE: {"name": "Chinese", "native_name": "中文", "flag": "🇨🇳"},
        Language.SPANISH: {"name": "Spanish", "native_name": "Español", "flag": "🇪🇸"},
        Language.FRENCH: {"name": "French", "native_name": "Français", "flag": "🇫🇷"},
        Language.GERMAN: {"name": "German", "native_name": "Deutsch", "flag": "🇩🇪"},
        Language.JAPANESE: {"name": "Japanese", "native_name": "日本語", "flag": "🇯🇵"},
        Language.KOREAN: {"name": "Korean", "native_name": "한국어", "flag": "🇰🇷"},
        Language.ARABIC: {"name": "Arabic", "native_name": "العربية", "flag": "🇸🇦"},
        Language.HINDI: {"name": "Hindi", "native_name": "हिन्दी", "flag": "🇮🇳"},
    }

    DEFAULT_LANGUAGE = Language.RUSSIAN

    @classmethod
    def get_supported_languages(cls) -> Dict[str, Dict[str, str]]:
        """Get list of supported languages."""
        return cls.SUPPORTED_LANGUAGES

    @classmethod
    def is_supported(cls, language: str) -> bool:
        """Check if language is supported."""
        return language in cls.SUPPORTED_LANGUAGES

    @classmethod
    def get_language_info(cls, language: str) -> Optional[Dict[str, str]]:
        """Get language information."""
        return cls.SUPPORTED_LANGUAGES.get(language)

    @classmethod
    def get_default_language(cls) -> str:
        """Get default language."""
        return cls.DEFAULT_LANGUAGE

    @classmethod
    def validate_language(cls, language: str) -> str:
        """Validate language and return valid language."""
        if cls.is_supported(language):
            return language
        return cls.DEFAULT_LANGUAGE

    @classmethod
    def get_language_list(cls) -> List[Dict[str, str]]:
        """Get list of languages for API."""
        return [
            {
                "code": code,
                "name": info["name"],
                "native_name": info["native_name"],
                "flag": info["flag"],
            }
            for code, info in cls.SUPPORTED_LANGUAGES.items()
        ]


language_manager = LanguageManager()
