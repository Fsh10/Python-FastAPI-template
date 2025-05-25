import uuid

from sqlalchemy import UUID, Column, ForeignKey, Integer, text

from src.constants import get_random_guid


class BaseCrudModel:
    """
    This class is made for universal controllers(routers in fastapi) and repositories
    You must override __tablename__ in child classes
    id - every model have id - so it can be there - also discussable if it should be NOT NULL
    """

    __tablename__ = "BaseCrudModel"
    id = Column(Integer, primary_key=True, index=True)


class UUIDIDMixin(object):
    id = Column(UUID, primary_key=True, nullable=False, default=uuid.uuid4)


class UUIDMixin(object):
    uuid = Column(
        UUID,
        unique=True,
        nullable=False,
        default=get_random_guid,
        server_default=text("uuid_generate_v4()"),
    )


class OrganizationIDMixin(object):
    organization_id = Column(
        UUID, ForeignKey("organization.id", ondelete="CASCADE"), nullable=False
    )
