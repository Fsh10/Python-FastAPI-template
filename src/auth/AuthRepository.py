import datetime
from typing import Optional

import jwt
from fastapi import Depends, Request
from fastapi_users import BaseUserManager, IntegerIDMixin, exceptions, models
from fastapi_users.jwt import decode_jwt, generate_jwt
from sqlalchemy import insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.exceptions import (
    ActivationKeyExpiredException,
    BadRequestException,
    BadTokenException,
    DefaultException,
    InvalidActivationKeyException,
    KeyNotFoundException,
    UserAlreadyExistsException,
    UserHasNotConfirmedException,
)
from src.notifications.NotificationModel import EventName, NotificationSettings
from src.organizations.OrganizationModel import Organization
from src.organizations.OrganizationRepository import get_organization_repository
from src.organizations.OrganizationSchemas import CreateOrganizationScheme
from src.selectors.SelectorsModels import UsedAttr
from src.selectors.SelectorsRouter import get_all_attrs
from src.users.UserModel import User, get_user_db
from src.users.UserSchemas import CreateUserScheme, CreateUserSchemeOut, GetUserScheme
from src.utils.decrypt import verify_access_key
from src.utils.managers.RabbitMQ.publisher import publisher
from src.utils.managers.time_manager import UTC_ISO_FORMAT


class UserManager(IntegerIDMixin, BaseUserManager[User, int]):
    reset_password_token_secret = settings.SECRET_AUTH
    verification_token_secret = settings.SECRET_AUTH

    def __init__(
        self, user_db, organization_repository=None, subscription_repository=None
    ):
        super().__init__(user_db)
        self._organization_repository = organization_repository
        self._subscription_repository = subscription_repository

    @property
    def organization_repository(self):
        if self._organization_repository is None:
            from src.organizations.OrganizationRepository import (
                get_organization_repository,
            )

            self._organization_repository = get_organization_repository()
        return self._organization_repository

    async def create(
        self,
        user_create: CreateUserSchemeOut,
        session: AsyncSession,
        safe: bool = False,
        request: Optional[Request] = None,
    ) -> models.UP:
        user_create = CreateUserScheme(**user_create.model_dump())
        await self.validate_password(user_create.password, user_create)

        existing_user = await self.user_db.get_by_email(user_create.email)
        user = existing_user

        if existing_user and existing_user.is_verified:
            raise UserAlreadyExistsException(
                message="User with this email already exists"
            )

        if not existing_user:
            password = user_create.password
            user_create.hashed_password = self.password_helper.hash(password)

            organization = await self.organization_repository.create_entity(
                CreateOrganizationScheme(name=user_create.organization_name),
                session=session,
            )

            user_create.organization_id = organization.id

            user = await self.user_db.create(user_create.model_dump())

            user.is_active = True

            await session.flush()

        await self.create_verification_link(user_create.email)

        return await self.get(user.id)

    @classmethod
    async def check_verify(cls, user: User, session: AsyncSession):
        if not user["is_verified"]:
            raise UserHasNotConfirmedException(message="You have not verified your email")
        events = [event_name.value for event_name in EventName]
        for event_name in events:
            if event_name == EventName.shift.value:
                await session.execute(
                    insert(NotificationSettings).values(
                        user_uuid=str(user.uuid),
                        event_name=event_name,
                        send=True,
                        is_disabled=True,
                    )
                )
            else:
                await session.execute(
                    insert(NotificationSettings).values(
                        user_uuid=str(user.uuid), event_name=event_name, send=True
                    )
                )
        return True

    @classmethod
    async def verify_user(cls, token: str, session: AsyncSession):
        try:
            data = decode_jwt(
                token,
                cls.verification_token_secret,
                [cls.verification_token_audience],
            )
        except jwt.PyJWTError:
            raise BadTokenException()

        try:
            output = data["arg"]
        except KeyError:
            raise BadTokenException()

        try:
            if output.isdigit():
                stmt = (
                    update(User.__table__)
                    .where(User.__table__.c.id == int(output))
                    .values(is_verified=True)
                )
            else:
                stmt = (
                    update(User.__table__)
                    .where(User.__table__.c.email == str(output))
                    .values(is_verified=True)
                )
            await session.execute(stmt)
            await session.commit()
            return {"message": "User has been verified successfully"}
        except KeyError:
            return {"message": "Verification link not found or has expired"}
        except Exception as e:
            raise e

    @classmethod
    async def create_verification_link(cls, user_email):
        def pattern(arg):
            token_data = {
                "arg": str(arg),
                "aud": cls.verification_token_audience,
            }

            token = generate_jwt(
                token_data,
                cls.verification_token_secret,
                cls.verification_token_lifetime_seconds,
            )
            return token

        if user_email:
            from src.utils.managers.SMTP.services.async_email_service import (
                AsyncEmailService,
            )

            await AsyncEmailService.send_account_activate_email(
                user_email=user_email,
                link="https://"
                + settings.DOMAIN_NAME
                + "/verify-email/"
                + pattern(user_email),
            )

            return {"status": 200, "data": "Email sent", "details": None}

    @classmethod
    async def activate_user(
        cls, activation_key: str, email: str, session: AsyncSession
    ):
        is_verified, days, _id = verify_access_key(activation_key)

        if not is_verified:
            raise InvalidActivationKeyException()

        response = await publisher.check_activation_key(
            activation_key_id=_id, activation_key=activation_key
        )

        if response.get("error", None):
            raise DefaultException()

        if response.get("expire_at", None):
            if (
                datetime.datetime.strptime(
                    response["expire_at"].strip(), UTC_ISO_FORMAT
                )
                < datetime.datetime.now()
            ):
                raise ActivationKeyExpiredException()

        try:
            end_date = datetime.datetime.now() + datetime.timedelta(days=days)
            used_key = await get_all_attrs(session)
            if activation_key not in used_key:
                await session.execute(
                    update(User.__table__)
                    .where(User.__table__.c.email == str(email))
                    .values(is_active=True)
                )
                await session.execute(insert(UsedAttr).values(attr=activation_key))

                user = await session.execute(
                    select(User).where(User.email == str(email))
                )

                user = user.scalar_one()
                organization = await session.get(Organization, user.organization_id)

                await publisher.activate_key(
                    activation_key=activation_key,
                    end_date=end_date,
                    organization_name=organization.name,
                )

                return {"message": "Account activated."}
            else:
                return {"message": "This key has already been used."}
        except KeyError:
            await session.rollback()
            raise KeyNotFoundException()
        except Exception as ex:
            await session.rollback()
            raise ex

    async def forgot_password(
        self, user: models.UP, request: Optional[Request] = None
    ) -> None:
        if not user.is_active:
            raise exceptions.UserInactive()

        token_data = {
            "sub": str(user.email),
            "password_fgpt": self.password_helper.hash(user.hashed_password),
            "aud": self.reset_password_token_audience,
        }
        token = generate_jwt(
            token_data,
            self.reset_password_token_secret,
            self.reset_password_token_lifetime_seconds,
        )
        if user.email:
            from src.utils.managers.SMTP.services.async_email_service import (
                AsyncEmailService,
            )

            await AsyncEmailService.send_password_reset_email(
                user.email, settings.DOMAIN_NAME + "/reset-password/" + token
            )

    async def reset_password(
        self,
        token: str,
        password: str,
        request: Optional[Request] = None,
        session: AsyncSession = None,
    ) -> models.UP:
        try:
            data = decode_jwt(
                token,
                self.reset_password_token_secret,
                [self.reset_password_token_audience],
            )
        except jwt.PyJWTError:
            raise exceptions.InvalidResetPasswordToken()

        try:
            user_email = data["sub"]
            password_fingerprint = data["password_fgpt"]
        except KeyError:
            raise exceptions.InvalidResetPasswordToken()

        user = await self.user_db.get_by_email(user_email)

        valid_password_fingerprint, _ = self.password_helper.verify_and_update(
            user.hashed_password, password_fingerprint
        )

        if not valid_password_fingerprint:
            raise exceptions.InvalidResetPasswordToken()

        if not user.is_active:
            raise exceptions.UserInactive()

        updated_user = await self._update(user, {"password": password})

        await self.on_after_reset_password(user, request)

        return updated_user

    async def change_password(
        self,
        request: Request,
        user: User,
        current_password: str,
        new_password: str,
        new_password_repeat: str,
    ):
        if not new_password == new_password_repeat:
            raise BadRequestException(message="New password does not match")

        valid_old_password, _ = self.password_helper.verify_and_update(
            current_password, user.hashed_password
        )

        if not valid_old_password:
            raise BadRequestException(message="Invalid current password")

        old_new_match, _ = self.password_helper.verify_and_update(
            new_password, user.hashed_password
        )

        if old_new_match:
            raise BadRequestException(
                message="New and current password must be different"
            )

        if not user.is_active:
            raise exceptions.UserInactive()

        updated_user = await self._update(user, {"password": new_password})

        await self.on_after_reset_password(user, request)

        return GetUserScheme(**updated_user.__dict__)


async def get_user_manager(
    user_db=Depends(get_user_db),
    organization_repository=Depends(get_organization_repository),
):
    yield UserManager(user_db, organization_repository)
