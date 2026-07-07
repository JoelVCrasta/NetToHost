import logging
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from supabase_auth import User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
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
    try:
        query = select(Organization).join(OrgMember).where(OrgMember.user_id == user.id)
        result = await session.execute(query)

        return result.all()
    except Exception as e:
        logger.error(f"Error fetching organizations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.post("/")
async def create_organization(
    payload: CreateOrganizationRequest,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    try:
        new_org = Organization(name=payload.name)
        session.add(new_org)
        await session.commit()
        await session.refresh(new_org)

        org_member = OrgMember(
            user_id=user.id, organization_id=new_org.id, role=MemberRole.OWNER
        )

        session.add(org_member)
        await session.commit()

        return {
            "id": new_org.id,
            "name": new_org.name,
            "message": "Organization created successfully.",
        }
    except IntegrityError as e:
        await session.rollback()
        logger.error(f"Integrity error creating organization: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid data provided."
        )
    except Exception as e:
        logger.error(f"Error creating organization: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.patch("/{organization_id}")
async def update_organization(
    organization_id: UUID,
    payload: UpdateOrganizationRequest,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    try:
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
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating organization: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.delete("/{organization_id}")
async def delete_organization(
    organization_id: UUID,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    try:
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
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting organization: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.post("/{organization_id}/members")
async def add_org_members(
    organization_id: UUID,
    payload: AddOrgMembersRequest,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    try:
        await verify_permission(
            organization_id, user.id, session, "add members to", [MemberRole.OWNER]
        )

        new_members = []
        for member in payload.members:
            new_member = OrgMember(
                organization_id=organization_id,
                user_id=member.id,
                role=member.role,
                joined_at=datetime.now(timezone.utc),
            )
            new_members.append(new_member)

        session.add_all(new_members)
        await session.commit()

        return {"message": "Members added successfully."}
    except HTTPException:
        raise
    except IntegrityError as e:
        await session.rollback()
        logger.error(f"Integrity error adding members: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid data provided."
        )
    except Exception as e:
        logger.error(f"Error adding members: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )


@router.patch("/{organization_id}/members")
async def update_org_member_role(
    organization_id: UUID,
    payload: UpdateOrgMemberRoleRequest,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    try:
        await verify_permission(
            organization_id, user.id, session, "update member role", [MemberRole.OWNER]
        )

        query = select(OrgMember).where(
            OrgMember.organization_id == organization_id,
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
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating member role: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )


@router.delete("/{organization_id}/members")
async def remove_org_members(
    organization_id: UUID,
    payload: RemoveOrgMembersRequest,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    try:
        await verify_permission(
            organization_id, user.id, session, "remove members from", [MemberRole.OWNER]
        )

        query = select(OrgMember).where(
            OrgMember.organization_id == organization_id,
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
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error removing members: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )
