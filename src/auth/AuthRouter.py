from uuid import UUID

from fastapi import APIRouter, Body, Depends, Path, Request
from fastapi.params import Query
from fastapi_users import exceptions
from fastapi_users.jwt import decode_jwt, generate_jwt
from fastapi_users.router.reset import RESET_PASSWORD_RESPONSES
from jwt import ExpiredSignatureError
from pydantic import EmailStr
from starlette import status

from src.auth.AuthRepository import UserManager, get_user_manager
from src.config import settings
from src.dependencies import CurrentUserDep, SessionDep
from src.exceptions import (
    InvalidPasswordException,
    LinkExpiredException,
    ResetPasswordBadTokenException,
    UserHasNotConfirmedException,
    UserNotFoundException,
)
from src.organizations.OrganizationModel import Organization
from src.organizations.OrganizationSchemas import GetOrganizationScheme
from src.users.UserRepository import get_user_repository
from src.users.UserRouter import router_user
from src.users.UserSchemas import GetUserScheme

auth_router = APIRouter(prefix="", tags=["Auth"])


@auth_router.get("/check", response_model=GetUserScheme)
async def get_current_user(
    user: CurrentUserDep,
    session: SessionDep,
):
    """Get current user information."""
    repository = get_user_repository()
    user_data = await repository.get_entity_from_db_by_id(user.uuid, session)
    return GetUserScheme.model_validate(user_data, from_attributes=True)


@auth_router.post("/invite")
async def generate_invite_link(
    user: CurrentUserDep,
    session: SessionDep,
):
    """Generate invite link for user registration."""
    token = generate_jwt(
        data={
            "organization_id": str(user.organization_id),
            "aud": "fastapi-users:auth",
        },
        secret=settings.SECRET_AUTH,
        lifetime_seconds=3600,
    )

    return f"https://{settings.DOMAIN_NAME}/registration?token={token}"


@auth_router.get("/invite")
async def check_invite_link(
    token: str,
    session: SessionDep,
):
    """Check and validate invite link token."""
    if token:
        try:
            payload = decode_jwt(
                encoded_jwt=token,
                secret=settings.SECRET_AUTH,
                audience=["fastapi-users:auth"],
            )
            organization = await session.get(Organization, payload["organization_id"])
        except ExpiredSignatureError:
            raise LinkExpiredException()
        except Exception as ex:
            raise LinkExpiredException(message="Invalid link", error=str(ex))

        return GetOrganizationScheme(**organization.__dict__)


@auth_router.get(
    "/auth/jwt",
)
async def get_jwt_token(
    user: CurrentUserDep,
):
    """Get JWT token for current user."""
    token_data = {
        "arg": str(user.id),
        "aud": settings.SECRET_AUTH,
    }

    token = generate_jwt(
        token_data,
        settings.SECRET_AUTH,
        10800,
    )

    return {"access_token": token, "token_type": "bearer"}


@auth_router.get("/is_verified/{user_id}", response_model=bool)
async def check_is_verified(
    session: SessionDep,
    user_id: UUID = Path(description="User UUID"),
):
    """Check if user is verified."""
    user = await router_user.service.repository.get_entity_from_db_by_id(
        user_id, session=session
    )
    return await UserManager.check_verify(user, session=session)


@auth_router.post("/verify/{jwt_token}")
async def verify_user(
    jwt_token: str,
    session: SessionDep,
):
    """Verify user email with JWT token."""
    return await UserManager.verify_user(jwt_token, session)


@auth_router.post("/activate")
async def activate_user(
    session: SessionDep,
    email: EmailStr = Query(..., alias="email"),
    activation_key: str = Query(..., alias="activation_key"),
):
    """Activate user account with activation key."""
    return await UserManager.activate_user(
        activation_key=activation_key, email=email, session=session
    )


@auth_router.post(
    "/forgot-password",
    status_code=status.HTTP_202_ACCEPTED,
    name="reset:forgot_password",
)
async def forgot_password(
    request: Request,
    email: EmailStr = Body(..., embed=True),
    user_manager: UserManager = Depends(get_user_manager),
):
    """Request password reset for user email."""
    try:
        user = await user_manager.get_by_email(email)
    except exceptions.UserNotExists:
        raise UserNotFoundException(message="User with this email does not exist")

    try:
        await user_manager.forgot_password(user, request)
    except exceptions.UserInactive:
        raise UserHasNotConfirmedException(message="You have not confirmed your email")

    return None


@auth_router.post(
    "/reset-password",
    name="reset:reset_password",
    responses=RESET_PASSWORD_RESPONSES,
)
async def reset_password(
    request: Request,
    token: str,
    session: SessionDep,
    password: str = Query(..., alias="password"),
    user_manager: UserManager = Depends(get_user_manager),
):
    """Reset user password with reset token."""
    try:
        return await user_manager.reset_password(token, password, request, session)
    except (
        exceptions.InvalidResetPasswordToken,
        exceptions.UserNotExists,
        exceptions.UserInactive,
    ):
        raise ResetPasswordBadTokenException()
    except exceptions.InvalidPasswordException as ex:
        raise InvalidPasswordException(error=ex)


@auth_router.post("/change_password", name="change:change_password")
async def change_password(
    request: Request,
    user: CurrentUserDep,
    current_password: str = Query(..., alias="password"),
    new_password: str = Query(..., alias="new_password"),
    new_password_repeat: str = Query(..., alias="new_password_repeat"),
    user_manager: UserManager = Depends(get_user_manager),
):
    """Change user password."""
    try:
        return await user_manager.change_password(
            request, user, current_password, new_password, new_password_repeat
        )
    except (
        exceptions.InvalidResetPasswordToken,
        exceptions.UserNotExists,
        exceptions.UserInactive,
    ) as ex:
        raise ResetPasswordBadTokenException()
    except exceptions.InvalidPasswordException as ex:
        raise InvalidPasswordException(error=ex)
