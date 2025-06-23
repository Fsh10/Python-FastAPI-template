from uuid import UUID

from sqlalchemy import and_, delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import async_session_maker
from src.dependencies import CurrentUserDep, SessionDep
from src.notifications.NotificationModel import (
    EventName,
    Notification,
    NotificationSettings,
)
from src.notifications.NotificationRepository import (
    NotificationRepository,
    get_notification_repository,
)
from src.notifications.NotificationSchemas import (
    CreateNotificationScheme,
    GetNotificationSettingsScheme,
    NotificationSchemas,
    notification_schemas,
)
from src.organizations.OrganizationService import (
    OrganizationService,
    get_organization_service,
)
from src.users.UserModel import User
from src.utils.base.BaseService import BaseService


class NotificationService(BaseService):
    def __init__(
        self,
        repository: NotificationRepository,
        schemas: NotificationSchemas,
        organization_service: OrganizationService,
    ) -> None:
        super().__init__(repository, schemas)
        self.organization_service = organization_service

    async def get_all_filtered_entities(self, filters, session: AsyncSession):
        filtered_notifications = (
            await self.repository.get_all_filtered_entities_from_db(
                session=session, filters=filters
            )
        )

        result = []
        for notification in filtered_notifications:
            if notification["created_by_user"] == notification["user_uuid"]:
                continue

            result.append(self.schemas.get_response_scheme(**notification))
        return result

    async def create_entity(
        self,
        create_notification_params: CreateNotificationScheme,
        session: AsyncSession,
    ):
        if create_notification_params.user_uuid:
            allow = await self.check_user_allow_send_event_name(
                user_id=create_notification_params.user_uuid,
                event_name=create_notification_params.event_name,
                event_type=create_notification_params.event_type,
                session=session,
            )

            if not allow:
                return

            await self.repository.create_entity_in_db(
                entity=self.schemas.create_request_scheme(
                    **create_notification_params.model_dump()
                ),
                session=session,
            )
            return

        employers_ids = await self.organization_service.get_employers_ids(
            organization_id=create_notification_params.organization_id,
            user_id=create_notification_params.created_by_user,
            session=session,
        )

        notifications_to_insert = []

        if not employers_ids:
            allow = await self.check_user_allow_send_event_name(
                user_id=create_notification_params.created_by_user,
                event_name=create_notification_params.event_name,
                event_type=create_notification_params.event_type,
                session=session,
            )

            if allow:
                create_notification_params.user_uuid = (
                    create_notification_params.created_by_user
                )

                notification_data = create_notification_params.model_dump()

                if not notification_data.get("organization_id"):
                    notification_data["organization_id"] = (
                        create_notification_params.organization_id
                    )
                notifications_to_insert.append(
                    self.schemas.create_request_scheme(**notification_data)
                )
        else:
            for _id in employers_ids:
                allow = await self.check_user_allow_send_event_name(
                    user_id=_id,
                    event_name=create_notification_params.event_name,
                    event_type=create_notification_params.event_type,
                    session=session,
                )

                if not allow:
                    continue

                create_notification_params.user_uuid = _id
                notification_data = create_notification_params.model_dump()
                if not notification_data.get("organization_id"):
                    notification_data["organization_id"] = (
                        create_notification_params.organization_id
                    )
                notifications_to_insert.append(
                    self.schemas.create_request_scheme(**notification_data)
                )

        await self.repository.create_many_in_db(
            entities=notifications_to_insert,
            session=session,
        )

    async def mark_all_as_read(
        self,
        session: SessionDep,
        user: CurrentUserDep,
    ):
        await self.repository._execute_query_without_result(
            query=update(Notification)
            .where(Notification.user_uuid == user.uuid)
            .values(is_read=True),
            session=session,
        )

    async def mark_as_read(
        self,
        notification_id: str,
        session: SessionDep,
        user: CurrentUserDep,
    ):
        return await self.repository._execute_query(
            query=update(Notification)
            .where(
                Notification.user_uuid == user.uuid, Notification.id == notification_id
            )
            .values(is_read=True)
            .returning(Notification.is_read),
            session=session,
        )

    async def delete_entity_by_id(
        self,
        notification_id: str,
        session: SessionDep,
        user: CurrentUserDep,
    ):
        # TODO: wrong layer
        await self.repository._execute_query_without_result(
            query=delete(Notification).where(
                and_(
                    Notification.id == notification_id,
                    Notification.user_uuid == user.uuid,
                )
            ),
            session=session,
        )

    async def delete_all(
        self,
        session: SessionDep,
        user: CurrentUserDep,
    ):
        # TODO: wrong layer
        await self.repository._execute_query_without_result(
            query=delete(Notification).where(Notification.user_uuid == user.uuid),
            session=session,
        )

    async def get_all_entities(
        self,
        session: SessionDep,
        user: CurrentUserDep,
    ):
        notifications = await self.repository.get_all_entities_from_db(
            query_parameters={"user_uuid": user.uuid}, session=session
        )

        return [
            self.schemas.get_response_scheme(**notification)
            for notification in notifications
        ]

    async def check_user_allow_send_event_name(
        self, user_id: UUID, event_name: str, event_type: str, session: AsyncSession
    ):
        return await self.repository._execute_query(
            query=select(NotificationSettings.send).where(
                and_(
                    NotificationSettings.user_uuid == user_id,
                    NotificationSettings.event_name == event_name,
                    NotificationSettings.event_type == event_type,
                )
            ),
            session=session,
        )

    async def get_user_notification_settings(
        self,
        session: SessionDep,
        user: CurrentUserDep,
    ):
        return [
            GetNotificationSettingsScheme(**notification.__dict__)
            for notification in await self.repository._execute_query_scalar_all(
                query=select(NotificationSettings)
                .where(NotificationSettings.user_uuid == str(user.uuid))
                .order_by(NotificationSettings.event_name),
                session=session,
            )
        ]

    async def toggle_notification(
        self,
        event_name: str,
        event_type: str,
        session: SessionDep,
        user: CurrentUserDep,
    ):
        user_notification: NotificationSettings = await self.repository._execute_query(
            select(NotificationSettings).where(
                NotificationSettings.user_uuid == str(user.uuid),
                NotificationSettings.event_name == event_name,
                NotificationSettings.event_type == event_type,
            ),
            session=session,
        )

        user_notification.send = not user_notification.send
        return user_notification.send

    async def create_user_notifications(self):
        events = [
            ("SENSOR_BOX", "DELETE"),
            ("SENSOR_BOX", "CREATE"),
            ("SHIFT", "ASSIGNED"),
            ("TEAM", "CREATE"),
            ("TEAM", "ASSIGNED"),
            ("COMMENT", "CREATE"),
            ("EQUIPMENT", "CREATE"),
            ("EQUIPMENT", "DELETE"),
        ]

        session: AsyncSession
        async with async_session_maker() as session:
            user_ids = (await session.execute(select(User.uuid))).scalars().all()
            for user_id in user_ids:
                for event in events:
                    exists = (
                        (
                            await session.execute(
                                select(NotificationSettings).where(
                                    and_(
                                        and_(
                                            NotificationSettings.user_uuid == user_id,
                                            NotificationSettings.event_name == event[0],
                                        ),
                                        NotificationSettings.event_type == event[1],
                                    )
                                )
                            )
                        )
                        .scalars()
                        .all()
                    )

                    if exists:
                        continue

                    if event[0] == EventName.shift.value:
                        await session.execute(
                            insert(NotificationSettings).values(
                                user_uuid=user_id,
                                event_name=event[0],
                                event_type=event[1],
                                send=True,
                                is_disabled=True,
                            )
                        )
                        await session.flush()
                    else:
                        await session.execute(
                            insert(NotificationSettings).values(
                                user_uuid=user_id,
                                event_name=event[0],
                                event_type=event[1],
                                send=True,
                            )
                        )
                        await session.flush()
                    await session.commit()


def get_notification_service() -> NotificationService:
    repository = get_notification_repository()
    organization_service = get_organization_service()
    return NotificationService(
        repository=repository,
        schemas=notification_schemas,
        organization_service=organization_service,
    )
