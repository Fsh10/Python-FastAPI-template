import abc
import asyncio
from typing import Any, Dict, List, Optional, Tuple, Type, Union
from uuid import UUID

from pydantic import BaseModel
from sqlalchemy import and_, delete, func, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import class_mapper
from starlette.responses import JSONResponse

from src.database import Base
from src.exceptions import NotFoundException
from src.utils.base.BaseCrudModel import BaseCrudModel
from src.utils.decorators import catch_error, logged


class BaseRepository(abc.ABC):
    """
    Base repository class for handling basic CRUD operations for REST APIs.
    Implementations should define a specific model.
    """

    model: Type[BaseCrudModel]

    def get_model_name(self) -> str:
        """Return the table name of the model."""
        return self.model.__tablename__

    @catch_error
    @logged
    async def get_entity_from_db_by_id(
        self,
        entity_id: int | str,
        session: AsyncSession,
        recursive_depth: int = 4,
    ) -> Optional[Dict[str, Any]]:
        """Fetch an entity by its ID."""
        if hasattr(self.model, "uuid") and hasattr(self.model, "id"):
            if self.model.id.type.python_type == UUID:
                try:
                    if isinstance(entity_id, str):
                        entity_id = UUID(entity_id)
                except ValueError:
                    return None

        return await self.__get_one_recursive(
            self.model, entity_id, session, recursive_depth
        )

    @catch_error
    @logged
    async def get_entity_from_db_by_uuid(
        self,
        entity_uuid: UUID | str,
        session: AsyncSession,
        recursive_depth: int = 4,
    ) -> Optional[Dict[str, Any]]:
        """Fetch an entity by its UUID."""
        if hasattr(self.model, "uuid"):
            return await self._execute_query_one_or_none(
                select(self.model).where(self.model.uuid == entity_uuid),
                session=session,
            )
        else:
            return await self._execute_query_one_or_none(
                select(self.model).where(self.model.id == entity_uuid), session=session
            )

    @catch_error
    @logged
    async def get_all_filtered_entities_from_db(
        self, session: AsyncSession, filters: Dict[str, Any], recursive_depth: int = 4
    ) -> List[Dict[str, Any]]:
        """Fetch all entities with filters applied."""
        return await self.__get_filtered_recursive(session, recursive_depth, filters)

    @catch_error
    @logged
    async def get_all_entities_from_db(
        self,
        session: AsyncSession,
        query_parameters: Dict[str, Union[int, List[int]]] | None = None,
        recursive_depth: int = 4,
    ) -> List[Dict[str, Any]]:
        """Fetch all entities from the database."""
        return await self.__get_all_recursive(
            session, query_parameters, recursive_depth
        )

    @catch_error
    @logged
    async def count_all_entities(self, session: AsyncSession, query_parameters=None):
        """Count all entities matching query parameters."""
        query = select(func.count()).select_from(self.model)

        if query_parameters:
            filters_raw: list = []
            filters = self._process_filters_of_query_parameters(
                filters_raw, query_parameters
            )

            if filters:
                query = query.filter(*filters)

        return await self._execute_query(query=query, session=session)

    @catch_error
    @logged
    async def create_entity_in_db(
        self, entity: BaseModel, session: AsyncSession
    ) -> Optional[Dict[str, Any]]:
        """Create a new entity in the database."""
        result = await session.execute(
            insert(self.model).values(**entity.model_dump()).returning(self.model.id)
        )
        entity_from_db_id = result.scalar()

        await session.flush()

        if hasattr(self.model, "uuid") and self.model.id.type.python_type == UUID:
            created_entity = await self._execute_query_one_or_none(
                select(self.model).where(self.model.id == entity_from_db_id),
                session=session,
            )
            if created_entity:
                return self.__object_as_dict(created_entity)
            else:
                return await self.__get_one_recursive(
                    self.model, entity_from_db_id, session
                )
        else:
            return await self.__get_one_recursive(
                self.model, entity_from_db_id, session
            )

    async def create_many_in_db(self, entities: List[BaseModel], session: AsyncSession):
        """Create multiple entities in the database."""
        return await self._execute_query_scalar_all(
            insert(self.model)
            .values([entity.model_dump() for entity in entities])
            .returning(self.model),
            session=session,
        )

    @catch_error
    @logged
    async def update_entity_in_db(
        self, entity_id: int | str, entity: BaseModel, session: AsyncSession
    ) -> Optional[Dict[str, Any]]:
        """Update an existing entity in the database (partial update)."""
        if hasattr(self.model, "uuid"):
            try:
                if isinstance(entity_id, str):
                    entity_id = UUID(entity_id)
                result = await session.execute(
                    select(self.model).where(self.model.uuid == entity_id)
                )
                entity_from_db = result.scalar_one_or_none()
            except ValueError:
                raise NotFoundException(message=f"Invalid UUID format: {entity_id}")
        else:
            if isinstance(entity_id, str) and entity_id.isdigit():
                entity_id = int(entity_id)
            entity_from_db = await session.get(self.model, entity_id)

        if entity_from_db is None:
            raise NotFoundException(message=f"Entity with id {entity_id} not found")

        update_data = {
            k: v
            for k, v in entity.model_dump(exclude_unset=True).items()
            if v is not None
        }
        if not update_data:
            return await self.__get_one_recursive(self.model, entity_id, session)

        if hasattr(self.model, "uuid"):
            try:
                if isinstance(entity_id, str):
                    entity_id = UUID(entity_id)
                result = await session.execute(
                    update(self.model)
                    .where(self.model.uuid == entity_id)
                    .values(**update_data)
                    .returning(self.model.uuid)
                )
                result.scalar()
            except ValueError:
                raise NotFoundException(message=f"Invalid UUID format: {entity_id}")
        else:
            if isinstance(entity_id, str) and entity_id.isdigit():
                entity_id = int(entity_id)

            result = await session.execute(
                update(self.model)
                .where(self.model.id == entity_id)
                .values(**update_data)
                .returning(self.model.id)
            )
            result.scalar()

        await session.flush()

        return await self.__get_one_recursive(self.model, entity_id, session)

    @catch_error
    @logged
    async def delete_entity_from_db_by_id(
        self, entity_id: int | str | UUID, session: AsyncSession
    ) -> JSONResponse:
        """Delete an entity by its ID."""

        entity_from_db = await self.__get_entity_by_id_or_uuid(
            entity_id=entity_id, model=self.model, session=session
        )

        if entity_from_db is None:
            raise NotFoundException(message=f"Entity with id {entity_id} not found")

        if hasattr(self.model, "uuid"):
            try:
                if isinstance(entity_id, str):
                    entity_id = UUID(entity_id)
                await session.execute(
                    delete(self.model).where(self.model.uuid == entity_id)
                )
            except ValueError:
                raise NotFoundException(message=f"Invalid UUID format: {entity_id}")
        else:
            if isinstance(entity_id, str) and entity_id.isdigit():
                entity_id = int(entity_id)
            await session.execute(delete(self.model).where(self.model.id == entity_id))
        return JSONResponse(content=None, status_code=204)

    async def __get_all_recursive(
        self,
        session: AsyncSession,
        query_parameters: Dict[str, Union[int, List[int]]] = None,
        recursive_depth: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Recursively fetch all entities and their sub-entities.
        """
        if hasattr(self.model, "uuid") and self.model.id.type.python_type == UUID:
            query = select(self.model.id)
        else:
            query = select(self.model.id)
        filters_raw: list = []

        if query_parameters:
            filters = self._process_filters_of_query_parameters(
                filters_raw, query_parameters
            )

            if filters:
                query = query.filter(*filters)

                limit = query_parameters.get("limit", None)
                offset = query_parameters.get("offset", None)

            if offset and limit:
                query = query.offset(offset * limit)
            elif limit:
                query = query.limit(limit)
            elif offset:
                query = query.offset(offset)

        all_db_entities_ids = await self._execute_query_scalar_all(query, session)
        return [
            await self.__get_one_recursive(
                self.model, entity_id, session, recursive_depth
            )
            for entity_id in all_db_entities_ids
        ]

    async def __get_filtered_recursive(
        self,
        session: AsyncSession,
        recursive_depth: int = 5,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Recursively fetch filtered entities and their sub-entities.
        """
        query = select(self.model)

        if filters:
            filter_conditions = [
                getattr(self.model, key) == value
                for key, value in filters.items()
                if hasattr(self.model, key)
            ]
            if filter_conditions:
                query = query.where(and_(*filter_conditions))

        all_entities = await self._execute_query_scalar_all(query, session)

        if hasattr(self.model, "uuid") and self.model.id.type.python_type == UUID:
            return [
                await self.__get_one_recursive(
                    self.model, entity.id, session, recursive_depth
                )
                for entity in all_entities
            ]
        else:
            return [
                await self.__get_one_recursive(
                    self.model, entity.id, session, recursive_depth
                )
                for entity in all_entities
            ]

    async def __get_one_recursive(
        self,
        model: Type[BaseCrudModel],
        item_id: int | str | UUID,
        session: AsyncSession,
        recursive_depth: int = 2,
    ) -> Optional[Dict[str, Any]]:
        """
        Recursively gets entity - and after it get sub-entities of it (sub_entity - if field ends with "_id")
        :param model: model that you work with, because of it recursive - second and further
        :param session: AsyncSession - object to already work with database
        :param recursive_depth: depth of recursion - how long it will take sub-entities - because of recursive it decrements every recursion call
        :return: json dictionary of entity with all sub-entities that needed
        """
        try:
            object_result = await self.__get_entity_by_id_or_uuid(
                entity_id=item_id, model=model, session=session
            )
        except Exception as e:
            return None

        if object_result is None:
            return None

        json_result = self.__object_as_dict(object_result)
        jsons_to_add_to_final_result: List[Tuple[str, Any]] = []

        if recursive_depth > 0:
            for column, value in json_result.items():
                if self._is_model_id_or_uuid(column):
                    column_name: str = "_".join(column.split("_")[0:-1])
                    model = await self.__get_model_by_name(column_name)

                    if model is not None:
                        sub_json: dict = await self.__get_one_recursive(
                            model, value, session, recursive_depth=recursive_depth - 1
                        )

                        jsons_to_add_to_final_result.append([column_name, sub_json])

                elif self._is_model_ids_or_uuids(column):
                    column_name: str = "_".join(column.split("_")[0:-1])
                    model = await self.__get_model_by_name(column_name)
                    column_name += "s"
                    if value is not None:
                        sub_jsons = await asyncio.gather(
                            *[
                                self.__get_one_recursive(
                                    model=model,
                                    item_id=val,
                                    session=session,
                                    recursive_depth=recursive_depth - 1,
                                )
                                for val in value
                                if val is not None
                            ]
                        )

                        jsons_to_add_to_final_result.append((column_name, sub_jsons))

        self.__add_fields_to_json(json_result, jsons_to_add_to_final_result)
        return json_result

    async def __get_entity_by_id_or_uuid(
        self,
        entity_id: str | int | UUID,
        model: Type[BaseCrudModel],
        session: AsyncSession,
    ):
        if hasattr(model, "uuid") and hasattr(model, "id"):
            if model.id.type.python_type == UUID:
                try:
                    if isinstance(entity_id, str):
                        entity_id = UUID(entity_id)
                    entity = await self._execute_query_one_or_none(
                        select(model).where(model.id == entity_id), session=session
                    )
                except ValueError:
                    return None
            else:
                if isinstance(entity_id, str):
                    try:
                        entity_id = UUID(entity_id)
                        entity = await self._execute_query_one_or_none(
                            select(model).where(model.uuid == entity_id),
                            session=session,
                        )
                    except ValueError:
                        if entity_id.isdigit():
                            entity_id = int(entity_id)
                            entity = await self._execute_query_one_or_none(
                                select(model).where(model.id == entity_id),
                                session=session,
                            )
                        else:
                            return None
                elif isinstance(entity_id, int):
                    entity = await self._execute_query_one_or_none(
                        select(model).where(model.id == entity_id),
                        session=session,
                    )
                else:
                    entity = await self._execute_query_one_or_none(
                        select(model).where(model.uuid == entity_id), session=session
                    )
        else:
            if isinstance(entity_id, str) and entity_id.isdigit():
                entity_id = int(entity_id)
            entity = await self._execute_query_one_or_none(
                select(model).where(model.id == entity_id), session=session
            )

        return entity

    async def get_all_entity_ids(
        self,
        session: AsyncSession,
        query_parameters: Dict[str, Union[int, List[int]]] | None = None,
    ):
        if hasattr(self.model, "uuid"):
            query = select(self.model.uuid)
        else:
            query = select(self.model.id)
        filters_raw = []

        filters = self._process_filters_of_query_parameters(
            filters_raw, query_parameters
        )

        if filters:
            query = query.filter(*filters)

        return await self._execute_query_scalar_all(query=query, session=session)

    @staticmethod
    def __add_fields_to_json(
        json_obj: Dict[str, Any], fields_to_add: List[Tuple[str, Any]]
    ) -> None:
        """Add additional fields to a JSON object."""
        for column_name, sub_json in fields_to_add:
            if sub_json is not None:
                json_obj[column_name] = sub_json

    @staticmethod
    def __object_as_dict(obj: BaseCrudModel) -> Dict[str, Any]:
        """Convert an object to a dictionary."""
        mapper = class_mapper(obj.__class__)
        return {column.key: getattr(obj, column.key) for column in mapper.columns}

    @staticmethod
    def _is_model_id_or_uuid(column_name: str) -> bool:
        """Check if the column name represents a single ID."""
        return column_name.endswith("id") or column_name.endswith("uuid")

    @staticmethod
    def _is_model_ids_or_uuids(column_name: str) -> bool:
        """Check if the column name represents multiple IDs."""
        return column_name.endswith("ids") or column_name.endswith("uuids")

    @staticmethod
    async def __get_model_by_name(model_name: str) -> Type[BaseCrudModel]:
        """Retrieve the model class by its table name."""
        models = {cls.__name__: cls for cls in Base.__subclasses__()}
        splitted_model_name = model_name.split("_")
        model_name = "".join([i.capitalize() for i in splitted_model_name])
        return models.get(model_name)

    def _process_filters_of_query_parameters(
        self, filters, query_parameters: Dict[str, Union[int, List[int]]] | None = None
    ):
        """Process query parameters and convert them to SQLAlchemy filters."""
        if not query_parameters:
            return filters

        processed_params = query_parameters.copy()

        if processed_params.get("user_id") and hasattr(self.model, "user_uuid"):
            user_id = processed_params.get("user_id")
            filters.append(self.model.user_uuid == user_id)
            del processed_params["user_id"]

        for param, value in processed_params.items():
            if isinstance(value, UUID):
                value = str(value)
            elif isinstance(value, list):
                value = [str(v) if isinstance(v, UUID) else v for v in value]
            if self._is_model_id_or_uuid(param):
                if value is None:
                    filters.append(getattr(self.model, param).is_(None))
                elif type(value) == list:
                    filters.append(getattr(self.model, param).in_(value))
                else:
                    filters.append(getattr(self.model, param) == value)

            if self._is_model_ids_or_uuids(param):
                filters.append(
                    getattr(self.model, param).any(value)
                    if self.model.__dict__.get(param)
                    else getattr(self.model, param[0:-1]).in_(value)
                )

            if type(processed_params.get(param)) == bool:
                filters.append(getattr(self.model, param) == value)

        if query_parameters.get("time_start") or query_parameters.get("time_finish"):
            if query_parameters.get("time_start"):
                time_start = self.parse_datetime(
                    str(query_parameters.get("time_start"))
                )
                filters.append(
                    self.model.datetime_start >= time_start
                    if self.model.__dict__.get("datetime_start")
                    else self.model.time_start >= time_start
                )
            if query_parameters.get("time_finish"):
                time_finish = self.parse_datetime(
                    str(query_parameters.get("time_finish"))
                )
                filters.append(
                    self.model.datetime_finish <= time_finish
                    if self.model.__dict__.get("datetime_finish")
                    else self.model.time_finish <= time_finish
                )

        return filters

    @staticmethod
    async def _execute_query(query, session: AsyncSession) -> Any:
        """Execute query and return scalar result."""
        result = await session.execute(query)
        return result.scalar()

    @staticmethod
    async def _execute_query_one_or_none(query, session: AsyncSession) -> Any | None:
        """Execute query and return one result or None."""
        result = await session.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def _execute_query_scalar_all(query, session: AsyncSession) -> List[Any]:
        """Execute query and return all scalar results."""
        result = await session.execute(query)
        return result.scalars().all()

    @staticmethod
    async def _execute_query_without_result(query, session: AsyncSession) -> None:
        """Execute query without returning result."""
        await session.execute(query)


def get_base_repository() -> BaseRepository:
    return BaseRepository()
