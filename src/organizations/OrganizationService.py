from typing import Dict, List, Union
from uuid import UUID as UUIDType

from fastapi import File, Response, UploadFile
from influxdb_client.domain.organization import Organization
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.dependencies import CurrentUserDep, SessionDep
from src.exceptions import (
    BadRequestException,
    InternalServerErrorException,
    NotFoundException,
    PermissionDeniedException,
)
from src.organizations.OrganizationRepository import (
    OrganizationRepository,
    get_organization_repository,
)
from src.organizations.OrganizationSchemas import (
    OrganizationSchemas,
    organization_schemas,
)
from src.utils.base.BaseService import BaseService
from src.utils.managers import FileManager


def _ensure_uuid(value):
    """Convert value to UUID if necessary."""
    if isinstance(value, UUIDType):
        return value
    try:
        return UUIDType(value)
    except (ValueError, TypeError):
        raise BadRequestException(message=f"Invalid UUID format: {value}")


class OrganizationService(BaseService):
    """Service for organization operations."""
    
    def __init__(
        self, repository: OrganizationRepository, schemas: OrganizationSchemas
    ) -> None:
        """Initialize organization service."""
        super().__init__(repository, schemas)

    async def _get_by_name(self, name: str, session: AsyncSession):
        """Get organization by name."""
        result = await self.repository._execute_query(
            query=select(self.repository.model).where(
                self.repository.model.name == name
            ),
            session=session,
        )
        return result

    async def upload_avatar(
        self,
        organization_id: str,
        session: SessionDep,
        user: CurrentUserDep,
        file: UploadFile = File(...),
    ):
        """Upload organization avatar."""
        try:
            org_uuid = _ensure_uuid(organization_id)
        except ValueError:
            raise BadRequestException(
                message=f"Invalid UUID format: {organization_id}"
            )

        organization = await session.get(Organization, org_uuid)
        if not organization:
            raise NotFoundException(
                message=f"Organization with id {organization_id} not found"
            )

        old_file_link = organization.avatar

        file_link = await FileManager.upload_file(
            file=file,
            old_file_link=old_file_link if old_file_link else None,
            folder="organization_avatar",
        )
        organization.avatar = file_link
        return Response(content=file_link)

    async def delete_avatar(
        self,
        session: SessionDep,
        organization_id: str,
        user: CurrentUserDep,
    ):
        """Delete organization avatar."""
        try:
            org_uuid = _ensure_uuid(organization_id)
        except ValueError:
            raise BadRequestException(
                message=f"Invalid UUID format: {organization_id}"
            )

        organization = await session.get(Organization, org_uuid)
        if not organization:
            raise NotFoundException(
                message=f"Organization with id {organization_id} not found"
            )

        if organization.avatar:
            await FileManager.delete_file(
                file_name=organization.avatar.split("/", 4)[-1]
            )
            organization.avatar = None
            await session.flush()
        else:
            raise NotFoundException(message="Organization avatar not found")

    async def get_all_entities(
        self,
        session: SessionDep,
        query_parameters: Dict[str, Union[int, List[int]]] = None,
        recursive_depth: int = 4,
    ) -> List[BaseModel]:
        """Fetch all organizations from the database without organization_id filtering."""
        try:
            all_entities = await self.repository.get_all_entities_from_db(
                session=session,
                query_parameters=None,
                recursive_depth=recursive_depth,
            )
            return [
                self.schemas.get_response_scheme(**entity) for entity in all_entities
            ]
        except Exception as ex:
            raise BadRequestException(error=str(ex))

    async def update_entity(
        self,
        entity_id: int | str,
        entity: BaseModel,
        user: CurrentUserDep,
        session: SessionDep,
    ) -> BaseModel:
        """Update an existing organization in the database without organization_id."""
        try:
            updated_entity_data = await self.repository.update_entity_in_db(
                entity_id=entity_id, entity=entity, session=session
            )

            if updated_entity_data is None:
                raise NotFoundException()

            return self.schemas.get_response_scheme(**updated_entity_data)

        except ValueError as ve:
            raise BadRequestException(error=str(ve))

    async def get_all_by_api_key(
        self,
        api_key: str,
        session: SessionDep,
    ):
        """Get all organizations by API key."""
        if api_key != settings.SECRET_AUTH:
            raise PermissionDeniedException()

        try:
            all_entities = await self.repository.get_all_entities_from_db(
                session=session,
                query_parameters=None,
                recursive_depth=4,
            )
            return [
                {"uuid": str(entity.get("uuid") or entity.get("id"))}
                for entity in all_entities
            ]
        except Exception as ex:
            raise InternalServerErrorException(
                message="Error getting organization list", error=str(ex)
            )


def get_organization_service() -> OrganizationService:
    """Get organization service instance."""
    repository = get_organization_repository()
    return OrganizationService(repository=repository, schemas=organization_schemas)
