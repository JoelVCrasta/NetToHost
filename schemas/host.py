from pydantic import BaseModel


class UpdateHostNameRequest(BaseModel):
    name: str
    