from pydantic import BaseModel


class UserRegInfoSchema(BaseModel):
    email: str
    password: str


class CustomMessageSchema(BaseModel):
    from_fio: str
    to: str
    subject: str
    message: str


class CustomReportSchema(BaseModel):
    to: str


class AlertSchema(BaseModel):
    level: str
    message: str
    ip: str
    source_timestamp: str
    name: str
