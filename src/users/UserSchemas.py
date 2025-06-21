from typing import Optional
from uuid import UUID

from fastapi_users import schemas
from pydantic import BaseModel, EmailStr, Field, field_validator

from src.utils.base.BaseSchemasForRouter import BaseSchemasForRouter
from src.utils.managers.language_manager import language_manager

"""
WARNING: THIS IS JUST TEST SCHEMAS, CHANGE IT IN REAL PROJECT
"""


class UserSchemas(BaseSchemasForRouter):
    def __init__(self):
        super().__init__(
            get_response_scheme=GetUserScheme,
            create_request_scheme=CreateUserScheme,
            update_request_scheme=UpdateUserScheme,
        )


class GetUserShortScheme(BaseModel):
    uuid: str | UUID
    first_name: str
    last_name: str


class GetUserScheme(BaseModel):
    uuid: str | UUID
    first_name: str
    last_name: str
    full_name: str
    email: str
    avatar: Optional[str] = None
    phone: Optional[str] = None
    is_superuser: bool
    is_active: bool = False
    organization_id: Optional[str | UUID] = None
    time_zone: str
    language: str

    class ConfigDict:
        from_attributes = True


class GetUserSchemeRestricted(BaseModel):
    uuid: str | UUID
    first_name: str
    last_name: str
    email: str
    avatar: str
    phone: Optional[str] = None
    is_superuser: bool
    language: str

    class ConfigDict:
        from_attributes = True


class CreateUserSchemeOut(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1)
    first_name: str
    last_name: str
    phone: Optional[str] = None
    organization_name: str
    language: str = "ru"

    @field_validator("language")
    def validate_language(cls, v):
        """Validator for language field."""
        return language_manager.validate_language(v)


class CreateUserScheme(schemas.BaseUserCreate, CreateUserSchemeOut):
    password: str = Field(min_length=1, max_length=20, exclude=True)
    organization_id: Optional[str] = None
    organization_name: str = Field(exclude=True)
    hashed_password: Optional[str | bytes] = None


class UpdateUserScheme(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    organization_id: Optional[str | UUID] = None
    language: Optional[str] = None

    @field_validator("language")
    def validate_language(cls, v):
        """Validator for language field."""
        if v is None:
            return v
        return language_manager.validate_language(v)

    class ConfigDict:
        from_attributes = True


class LoginScheme(BaseModel):
    username: EmailStr
    password: str = Field(min_length=1)


class LanguageUpdateResponse(BaseModel):
    message: str
    language: str


user_schemas = UserSchemas()
GetUserScheme.model_rebuild()
