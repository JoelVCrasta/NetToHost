from uuid import UUID
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional


class CreateTokenRequest(BaseModel):
    name: str
    expires_at: Optional[datetime] = None


class UpdateTokenNameRequest(BaseModel):
    name: str


class UpdateTokenStatusRequest(BaseModel):
    is_active: bool


class TokenResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    org_id: UUID
    name: str
    is_active: bool
    created_by: UUID
    expires_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
