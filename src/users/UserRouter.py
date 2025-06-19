from typing import Dict, List, Optional
from uuid import UUID

from fastapi import Depends, File, HTTPException, UploadFile
from fastapi.routing import APIRoute
from fastapi_users.authentication import Strategy
from sqlalchemy import update
from starlette import status
from starlette.requests import Request
from starlette.responses import Response

from src.auth.AuthBackend import auth_backend
from src.auth.AuthRepository import UserManager, get_user_manager
from src.dependencies import CurrentUserDep, SessionDep
from src.exceptions import (
    UserBadCredentialsException,
    UserUnauthorizedException,
)
from src.users.UserModel import User
from src.users.UserSchemas import (
    CreateUserScheme,
    CreateUserSchemeOut,
    GetUserScheme,
    LanguageUpdateResponse,
    LoginScheme,
)
from src.users.UserService import get_user_service
from src.utils.base.BaseCrudRouter import BaseCrudRouter
from src.utils.managers import FileManager
from src.utils.managers.language_manager import language_manager
from src.utils.managers.translations import translations


class UserRouter(BaseCrudRouter):
    def __init__(self):
        super().__init__(prefix="", service=get_user_service(), tag="User")

        self.delete_api_route_if_exists(
            api_route_path=self.prefix + "/{entity_id}", http_method="DELETE"
        )

        self.delete_api_route_if_exists(
            api_route_path=self.prefix + "", http_method="POST"
        )

        self.rewrite_api_route(
            old_api_route_path=self.prefix,
            old_http_method="GET",
            new_route=APIRoute(
                path="",
                endpoint=self.service.get_all_entities,
                tags=[self.tag],
                response_model=Optional[List[self.service.schemas.get_response_scheme]],
                methods=["GET"],
            ),
        )


router_user = UserRouter()


@router_user.post(
    "/login",
    name=f"auth:{auth_backend.name}.login",
)
async def login(
    request: Request,
    credentials: LoginScheme,
    user_manager: UserManager = Depends(get_user_manager),
    strategy: Strategy[GetUserScheme, CreateUserScheme] = Depends(
        auth_backend.get_strategy
    ),
    requires_verification: bool = False,
):
    """Authenticate user and create login session."""
    user = await user_manager.authenticate(credentials)

    if user is None:
        raise UserBadCredentialsException(message="Invalid email or password")

    if not user.is_verified:
        raise UserUnauthorizedException(message="You have not verified your email")

    if requires_verification and not user.is_verified:
        raise UserUnauthorizedException()

    response = await auth_backend.login(strategy, user)

    await user_manager.on_after_login(user, request, response)

    return response


@router_user.post("/logout", name=f"auth:{auth_backend.name}.logout")
async def logout(
    request: Request,
    user: CurrentUserDep,
    strategy: Strategy[GetUserScheme, CreateUserScheme] = Depends(
        auth_backend.get_strategy
    ),
):
    """Logout current user and invalidate session."""
    token = request.cookies.get("Cookie_PV_data")
    if not token:
        raise HTTPException(status_code=401, detail="No token found")

    return await auth_backend.logout(strategy, user, token)


@router_user.get(
    "/languages",
    name="get_supported_languages",
    response_model=List[Dict[str, str]],
    tags=["User"],
    summary="Get list of supported languages",
    description="Returns list of all supported languages with their names and flags",
)
async def get_supported_languages():
    """Get list of supported languages."""
    return language_manager.get_language_list()


@router_user.put(
    "/language",
    name="update_user_language",
    response_model=LanguageUpdateResponse,
    tags=["User"],
    summary="Update user language",
    description="Updates user language",
)
async def update_user_language(
    language: str,
    user: CurrentUserDep,
    session: SessionDep,
):
    """Update user language."""
    validated_language = language_manager.validate_language(language)

    await router_user.service.repository._execute_query_without_result(
        query=update(User)
        .where(User.uuid == user.uuid)
        .values(language=validated_language),
        session=session,
    )

    return LanguageUpdateResponse(
        message=translations.get_message("language_updated", validated_language),
        language=validated_language,
    )


@router_user.post(
    "/create",
    response_model=router_user.service.schemas.get_response_scheme,
    status_code=status.HTTP_201_CREATED,
    name="register:register",
)
async def register(
    request: Request,
    session: SessionDep,
    user_create: CreateUserSchemeOut,
    user_manager: UserManager = Depends(get_user_manager),
):
    """Register new user."""
    created_user = await user_manager.create(
        user_create=user_create, safe=True, request=request, session=session
    )

    result = await router_user.service.repository.get_entity_from_db_by_id(
        str(created_user.uuid), session=session
    )

    return GetUserScheme.model_validate(result, from_attributes=True)


@router_user.post("/current_user/photo")
async def upload_photo(
    user: CurrentUserDep,
    session: SessionDep,
    photo: UploadFile = File(...),
):
    """Upload user photo."""
    old_photo_link = user.avatar

    file_link = await FileManager.upload_static_backend_file(
        file=photo,
        old_file_link=old_photo_link if old_photo_link else None,
        folder="user_photo",
    )
    user.avatar = file_link
    return Response(content=file_link)


@router_user.get("/current_user/photo")
async def get_photo(
    user: CurrentUserDep,
):
    """Get current user photo."""
    if not user.avatar:
        raise HTTPException(status_code=404, detail="User photo not found")

    return Response(content=user.avatar)


@router_user.delete("/current_user/photo")
async def delete_current_user_photo(
    user: CurrentUserDep,
):
    """Delete current user photo."""
    user.avatar = None
    return Response(content=None, status_code=200)


@router_user.get("/current_user")
async def get_current_user(
    user: CurrentUserDep,
):
    """Get current user information."""
    return user


@router_user.delete("/{user_id}")
async def delete_user(
    user_id: str | UUID,
    user: CurrentUserDep,
):
    """Delete user by ID."""
    return await router_user.service.delete_entity_by_id(entity_id=user_id, user=user)
