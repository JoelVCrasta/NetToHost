from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from models.model import OrgMember, MemberRole


async def verify_permission(
    organization_id: UUID,
    user_id: str,
    session: AsyncSession,
    action: str,
    required_role: list[MemberRole],
):
    member_query = select(OrgMember).where(
        OrgMember.organization_id == organization_id,
        OrgMember.user_id == user_id,
        OrgMember.role.in_(required_role),
    )
    member_result = await session.execute(member_query)

    if not member_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"You do not have permission to {action}.",
        )
