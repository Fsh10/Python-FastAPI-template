from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.utils.base.BaseRepository import BaseRepository
from src.utils.managers import S3_CLIENT


class UserRepository(BaseRepository):
    async def get_all_entities_from_db(
        self,
        session: AsyncSession,
        query_parameters: dict,
    ):
        query = select(self.model.uuid)

        filters_raw = []

        filters = self._process_filters_of_query_parameters(
            filters_raw, query_parameters
        )

        if filters:
            query = query.filter(*filters)

        query = query.order_by(self.model.first_name)

        ids = await self._execute_query_scalar_all(query, session)

        return ids

    @staticmethod
    async def delete_user_photo(user, photo_id: str):
        user.avatar = None
        await S3_CLIENT.delete_file(photo_id)


def get_user_repository() -> UserRepository:
    return UserRepository()
