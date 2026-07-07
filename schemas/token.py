from uuid import UUID
from pydantic import BaseModel, ConfigDict
from datetime import datetime


class CreateTokenRequest(BaseModel):
    name: str
    expires_at: datetime | None


class UpdateTokenNameRequest(BaseModel):
    name: str


class UpdateTokenStatusRequest(BaseModel):
    is_active: bool


class TokenResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    is_active: bool
    created_by: UUID
    created_at: datetime
    expires_at: datetime | None
