from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import BOOLEAN, VARCHAR
from sqlalchemy.orm import relationship

from src.database import Base
from src.utils.base.BaseCrudModel import UUIDIDMixin


class Organization(UUIDIDMixin, Base):
    __tablename__ = "organization"

    name = Column(VARCHAR, unique=True, nullable=False)
    description = Column(VARCHAR, nullable=True)
    avatar = Column(VARCHAR, nullable=True)
    is_configured = Column(BOOLEAN, nullable=False, server_default="TRUE")

    user = relationship(
        "User", back_populates="organization", cascade="all, delete-orphan"
    )

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True
