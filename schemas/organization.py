from pydantic import BaseModel
from uuid import UUID
from models.model import MemberRole


class Member(BaseModel):
    id: UUID
    role: MemberRole


class CreateOrganizationRequest(BaseModel):
    name: str


class UpdateOrganizationRequest(BaseModel):
    name: str


class AddOrgMembersRequest(BaseModel):
    members: list[Member]


class UpdateOrgMemberRoleRequest(BaseModel):
    user_id: UUID
    new_role: MemberRole


class RemoveOrgMembersRequest(BaseModel):
    user_ids: list[UUID]
