from typing import Dict

from src.utils.managers.language_manager import Language


class Translations:
    """Class for managing translations."""

    TRANSLATIONS = {
        Language.RUSSIAN: {
            "success": "Успешно",
            "error": "Ошибка",
            "not_found": "Не найдено",
            "unauthorized": "Не авторизован",
            "forbidden": "Доступ запрещен",
            "bad_request": "Неверный запрос",
            "validation_error": "Ошибка валидации",
            "user_not_found": "Пользователь не найден",
            "user_created": "Пользователь успешно создан",
            "user_updated": "Пользователь успешно обновлен",
            "user_deleted": "Пользователь успешно удален",
            "language_updated": "Язык успешно изменен",
            "invalid_credentials": "Неверная почта или пароль",
            "email_not_verified": "Вы не подтвердили почту",
            "organization_not_found": "Организация не найдена",
            "organization_created": "Организация успешно создана",
            "organization_updated": "Организация успешно обновлена",
            "organization_deleted": "Организация успешно удалена",
        },
        Language.ENGLISH: {
            "success": "Success",
            "error": "Error",
            "not_found": "Not found",
            "unauthorized": "Unauthorized",
            "forbidden": "Forbidden",
            "bad_request": "Bad request",
            "validation_error": "Validation error",
            "user_not_found": "User not found",
            "user_created": "User successfully created",
            "user_updated": "User successfully updated",
            "user_deleted": "User successfully deleted",
            "language_updated": "Language successfully updated",
            "invalid_credentials": "Invalid email or password",
            "email_not_verified": "You have not verified your email",
            "organization_not_found": "Organization not found",
            "organization_created": "Organization successfully created",
            "organization_updated": "Organization successfully updated",
            "organization_deleted": "Organization successfully deleted",
        },
        Language.CHINESE: {
            "success": "成功",
            "error": "错误",
            "not_found": "未找到",
            "unauthorized": "未授权",
            "forbidden": "禁止",
            "bad_request": "错误请求",
            "validation_error": "验证错误",
            "user_not_found": "用户未找到",
            "user_created": "用户创建成功",
            "user_updated": "用户更新成功",
            "user_deleted": "用户删除成功",
            "language_updated": "语言更新成功",
            "invalid_credentials": "邮箱或密码错误",
            "email_not_verified": "您尚未验证邮箱",
            "organization_not_found": "组织未找到",
            "organization_created": "组织创建成功",
            "organization_updated": "组织更新成功",
            "organization_deleted": "组织删除成功",
        },
    }

    @classmethod
    def get_message(cls, key: str, language: str = "en") -> str:
        """Get translated message."""
        if language not in cls.TRANSLATIONS:
            language = "en"

        return cls.TRANSLATIONS[language].get(key, key)

    @classmethod
    def get_all_messages(cls, language: str = "en") -> Dict[str, str]:
        """Get all messages for a language."""
        if language not in cls.TRANSLATIONS:
            language = "en"

        return cls.TRANSLATIONS[language]

    @classmethod
    def format_message(cls, key: str, language: str = "en", **kwargs) -> str:
        """Get formatted message with parameter substitution."""
        message = cls.get_message(key, language)
        return message.format(**kwargs)


translations = Translations()
