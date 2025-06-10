from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from src.utils.base.BaseSchemasForRouter import BaseSchemasForRouter

"""
WARNING: THIS IS JUST TEST SCHEMAS, CHANGE IT IN REAL PROJECT
"""


class OrganizationSchemas(BaseSchemasForRouter):
    def __init__(self):
        super().__init__(
            get_response_scheme=GetOrganizationScheme,
            create_request_scheme=CreateOrganizationScheme,
            update_request_scheme=UpdateOrganizationScheme,
        )


class GetOrganizationScheme(BaseModel):
    id: str | UUID
    name: str
    description: Optional[str] = None
    avatar: Optional[str] = None
    inn: Optional[str] = None
    kpp: Optional[str] = None
    is_configured: bool


class CreateOrganizationScheme(BaseModel):
    name: str
    description: Optional[str] = None
    inn: Optional[str] = None
    kpp: Optional[str] = None


class CreateFullOrganizationScheme(BaseModel):
    name: str
    description: Optional[str] = None
    inn: Optional[str] = None
    kpp: Optional[str] = None
    employees_count: Optional[int] = 1
    influx_address: Optional[str] = None
    influx_token: Optional[str] = None
    influx_org_name: Optional[str] = None
    influx_org_id: Optional[str] = None
    bucket: Optional[str] = None
    is_configured: Optional[bool] = True


class UpdateOrganizationScheme(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    inn: Optional[str] = None
    kpp: Optional[str] = None
    is_configured: Optional[bool] = True


organization_schemas = OrganizationSchemas()
