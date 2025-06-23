from typing import Any, Dict, List, Optional

from src.dependencies import CurrentUserDep, SessionDep
from src.utils.base.BaseService import BaseService

from ..auth.AuthService import AuthService, get_auth_service
from ..organizations.OrganizationService import (
    OrganizationService,
    get_organization_service,
)
from .UserRepository import UserRepository, get_user_repository
from .UserSchemas import UserSchemas, user_schemas


class UserService(BaseService):
    """Service for user operations."""
    
    def __init__(
        self,
        repository: UserRepository,
        schemas: UserSchemas,
        auth_service: AuthService,
        organization_service: OrganizationService,
    ) -> None:
        """Initialize user service."""
        super().__init__(repository, schemas)
        self.auth_service: AuthService = auth_service
        self.organization_service: OrganizationService = organization_service

    async def get_all_entities(
        self,
        session: SessionDep,
        user: CurrentUserDep,
        role_id: Optional[int] = None,
        unit_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Get all user entities with optional filtering."""
        query_parameters = self._parse_query_parameters(
            role_id=role_id, organization_id=user.organization_id, unit_uuid=unit_id
        )
        user_ids = await self.repository.get_all_entities_from_db(
            session,
            query_parameters,
        )

        return [
            await self.get_entity_by_id(entity_id=user_id, user=user, session=session)
            for user_id in user_ids
        ]


def get_user_service() -> UserService:
    """Get user service instance."""
    repository = get_user_repository()
    auth_service = get_auth_service()
    organization_service = get_organization_service()
    return UserService(
        repository=repository,
        schemas=user_schemas,
        auth_service=auth_service,
        organization_service=organization_service,
    )
