import logging
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from supabase_auth import User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from datetime import datetime, timezone

from main import get_session
from clients.supabase_client import get_current_user
from utils.permission import verify_permission
from models.model import Organization, OrgMember, MemberRole
from schemas.organization import (
    CreateOrganizationRequest,
    UpdateOrganizationRequest,
    AddOrgMembersRequest,
    UpdateOrgMemberRoleRequest,
    RemoveOrgMembersRequest,
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/")
async def get_organizations(
    user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)
):
    query = select(Organization).join(OrgMember).where(OrgMember.user_id == user.id)
    result = await session.execute(query)
    return result.all()

router.get("/{organization_id}")
async def get_organization(
    organization_id: UUID,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    query = select(Organization).where(Organization.id == organization_id)
    result = await session.execute(query)
    organization = result.scalar_one_or_none()

    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found."
        )

    return organization


@router.post("/")
async def create_organization(
    payload: CreateOrganizationRequest,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    new_org = Organization(name=payload.name)
    session.add(new_org)
    await session.flush()

    org_member = OrgMember(
        user_id=user.id, org_id=new_org.id, role=MemberRole.OWNER
    )
    session.add(org_member)
    await session.commit()

    return {
        "id": new_org.id,
        "name": new_org.name,
        "message": "Organization created successfully.",
    }


@router.patch("/{organization_id}")
async def update_organization(
    organization_id: UUID,
    payload: UpdateOrganizationRequest,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    query = select(Organization).where(Organization.id == organization_id)
    result = await session.execute(query)
    organization = result.scalar_one_or_none()

    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found."
        )

    await verify_permission(
        organization_id, user.id, session, "update", [MemberRole.OWNER]
    )

    organization.name = payload.name
    await session.commit()
    await session.refresh(organization)

    return {
        "id": organization.id,
        "name": organization.name,
        "message": "Organization updated successfully.",
    }


@router.delete("/{organization_id}")
async def delete_organization(
    organization_id: UUID,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    query = select(Organization).where(Organization.id == organization_id)
    result = await session.execute(query)
    organization = result.scalar_one_or_none()

    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found."
        )

    await verify_permission(
        organization_id, user.id, session, "delete", [MemberRole.OWNER]
    )

    await session.delete(organization)
    await session.commit()

    return {"message": "Organization deleted successfully."}


@router.post("/{organization_id}/members")
async def add_org_members(
    organization_id: UUID,
    payload: AddOrgMembersRequest,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    await verify_permission(
        organization_id, user.id, session, "add members to", [MemberRole.OWNER]
    )

    new_members = []
    for member in payload.members:
        new_member = OrgMember(
            org_id=organization_id,
            user_id=member.id,
            role=member.role,
            joined_at=datetime.now(timezone.utc),
        )
        new_members.append(new_member)

    session.add_all(new_members)
    await session.commit()

    return {"message": "Members added successfully."}


@router.patch("/{organization_id}/members")
async def update_org_member_role(
    organization_id: UUID,
    payload: UpdateOrgMemberRoleRequest,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    await verify_permission(
        organization_id, user.id, session, "update member role", [MemberRole.OWNER]
    )

    query = select(OrgMember).where(
        OrgMember.org_id == organization_id,
        OrgMember.user_id == payload.user_id,
    )
    result = await session.execute(query)
    member = result.scalar_one_or_none()

    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Member not found."
        )

    if member.user_id == user.id and payload.new_role != MemberRole.OWNER:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Self role change not allowed.",
        )

    member.role = payload.new_role
    await session.commit()
    await session.refresh(member)

    return {"message": "Member role updated successfully."}


@router.delete("/{organization_id}/members")
async def remove_org_members(
    organization_id: UUID,
    payload: RemoveOrgMembersRequest,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    await verify_permission(
        organization_id, user.id, session, "remove members from", [MemberRole.OWNER]
    )

    query = select(OrgMember).where(
        OrgMember.org_id == organization_id,
        OrgMember.user_id.in_(payload.user_ids),
    )
    result = await session.execute(query)
    members_to_remove = result.scalars().all()

    if not members_to_remove:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No members found to remove.",
        )

    for member in members_to_remove:
        if member.user_id == user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot remove yourself.",
            )
        await session.delete(member)

    await session.commit()

    return {"message": "Members removed successfully."}
