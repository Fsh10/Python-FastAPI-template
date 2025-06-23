from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.organizations.OrganizationModel import Organization
from src.utils.base.BaseRepository import BaseRepository


class OrganizationRepository(BaseRepository):
    """Repository for organization operations."""
    
    model = Organization

    async def _get_by_name(self, name: str, session: AsyncSession):
        """Get organization by name."""
        return await self._execute_query_one_or_none(
            select(self.model).where(self.model.name == name),
            session=session,
        )


def get_organization_repository() -> OrganizationRepository:
    """Get organization repository instance."""
    return OrganizationRepository()
