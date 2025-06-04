import abc
from typing import Dict, List, Optional, Union
from uuid import UUID

from fastapi import Depends
from pydantic import BaseModel
from sqlalchemy.exc import DatabaseError

from src.dependencies import CurrentUserDep, SessionDep
from src.exceptions import (
    BadRequestException,
    NotFoundException,
)
from src.utils.base.BaseCrudModel import BaseCrudModel
from src.utils.base.BaseRepository import BaseRepository, get_base_repository
from src.utils.base.BaseSchemasForRouter import BaseSchemasForRouter, get_base_schemas
from src.utils.decorators import logged


class BaseService(abc.ABC):
    def __init__(
        self,
        repository: BaseRepository,
        schemas: Optional[BaseSchemasForRouter],
    ) -> None:
        self.repository: BaseRepository = repository
        self.schemas: Optional[BaseSchemasForRouter] = schemas

    @logged
    async def get_entity_by_id(
        self,
        entity_id: int | str,
        session: SessionDep,
        user: CurrentUserDep,
    ) -> BaseModel:
        """Fetch an entity by its ID and return it as a schema."""
        entity_data = await self.repository.get_entity_from_db_by_id(
            entity_id=entity_id, session=session
        )

        if entity_data is None:
            raise NotFoundException()
        return self.schemas.get_response_scheme(**entity_data)

    @logged
    async def get_entity_by_uuid(
        self,
        entity_uuid: UUID | str,
        session: SessionDep,
        user: CurrentUserDep,
    ) -> BaseModel:
        """Fetch an entity by its UUID and return it as a schema."""
        entity_data = await self.repository.get_entity_from_db_by_uuid(
            entity_uuid=entity_uuid, session=session
        )

        if entity_data is None:
            raise NotFoundException()
        return self.schemas.get_response_scheme(**entity_data.__dict__)

    @logged
    async def get_all_entities(
        self,
        session: SessionDep,
        query_parameters: Dict[str, Union[int, List[int]]] = None,
        recursive_depth: int = 4,
    ) -> List[BaseModel]:
        """Fetch all entities from the database."""
        try:
            all_entities = await self.repository.get_all_entities_from_db(
                session=session,
                query_parameters=query_parameters,
                recursive_depth=recursive_depth,
            )
            return [
                self.schemas.get_response_scheme(**entity) for entity in all_entities
            ]
        except Exception as ex:
            raise BadRequestException(error=str(ex))

    @logged
    async def get_all_filtered_entities(
        self,
        session: SessionDep,
        query_parameters: Dict[str, Union[int, List[int]]] = None,
        recursive_depth: int = 4,
    ) -> List[BaseModel]:
        """Fetch all filtered entities from the database."""
        return await self.get_all_entities(
            session=session,
            query_parameters=query_parameters,
            recursive_depth=recursive_depth,
        )

    @logged
    async def get_all_entity_ids(
        self,
        session: SessionDep,
        query_parameters: Dict[str, Union[int, List[int]]] | None = None,
        recursive_depth: int = 4,
    ) -> List[int | UUID]:
        """Get all entity ids"""
        return await self.repository.get_all_entity_ids(
            query_parameters=query_parameters, session=session
        )

    @logged
    async def create_entity(
        self,
        entity: BaseModel,
        user: CurrentUserDep = None,
        session: SessionDep = None,
    ) -> BaseModel:
        """Create a new entity in the database."""
        if user and "organization_id" in entity.model_dump():
            entity.organization_id = user.organization_id

        try:
            entity_data = await self.repository.create_entity_in_db(
                entity=entity, session=session
            )
            return self.schemas.get_response_scheme(**entity_data)
        except ValueError as ex:
            raise BadRequestException(error=str(ex))

    @logged
    async def update_entity(
        self,
        entity_id: int | str,
        entity: BaseCrudModel,
        user: CurrentUserDep,
        session: SessionDep,
    ) -> BaseModel:
        """Update an existing entity in the database."""
        if hasattr(entity, "organization_id"):
            entity.organization_id = user.organization_id

        try:
            updated_entity_data = await self.repository.update_entity_in_db(
                entity_id=entity_id, entity=entity, session=session
            )

            if updated_entity_data is None:
                raise NotFoundException()

            return self.schemas.get_response_scheme(**updated_entity_data)

        except ValueError as ve:
            raise BadRequestException(error=str(ve))

    @logged
    async def delete_entity_by_id(
        self,
        entity_id: int | str,
        user: CurrentUserDep,
        session: SessionDep,
    ) -> None:
        """Delete an entity by its ID."""
        try:
            await self.repository.delete_entity_from_db_by_id(
                entity_id=entity_id, session=session
            )
            return None
        except DatabaseError as ex:
            raise BadRequestException(message="Error during deletion", error=str(ex))


def get_base_service(
    repository: BaseRepository = Depends(get_base_repository),
) -> BaseService:
    return BaseService(repository=repository, schemas=get_base_schemas())
