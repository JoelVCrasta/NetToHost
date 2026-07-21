from uuid import UUID
from pydantic import BaseModel

class CreateChatRequest(BaseModel):
    organization_id: UUID
    message: str
    is_private: bool = False
    