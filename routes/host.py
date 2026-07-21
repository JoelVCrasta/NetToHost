import logging
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from supabase_auth import User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from main import get_session
from clients.supabase_client import get_current_user
from utils.permission import verify_permission
from models.model import HostDevice, MemberRole
from schemas.host import UpdateHostNameRequest

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/{organization_id}/hosts")
async def get_hosts(
    organization_id: UUID,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    query = select(HostDevice).where(HostDevice.org_id == organization_id)
    result = await session.execute(query)
    hosts = result.scalars().all()
    return hosts


@router.patch("/{organization_id}/hosts/{host_id}")
async def update_host_name(
    organization_id: UUID,
    host_id: UUID,
    request: UpdateHostNameRequest,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    await verify_permission(
        organization_id,
        user.id,
        session,
        "update host name",
        [MemberRole.OWNER, MemberRole.ADMIN],
    )

    query = select(HostDevice).where(
        HostDevice.org_id == organization_id, HostDevice.id == host_id
    )
    result = await session.execute(query)
    host_device = result.scalar_one_or_none()

    if not host_device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Host not found"
        )

    host_device.name = request.name
    session.add(host_device)
    await session.commit()
    await session.refresh(host_device)

    return host_device


@router.delete("/{organization_id}/hosts/{host_id}")
async def remove_host(
    organization_id: UUID,
    host_id: UUID,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    await verify_permission(
        organization_id,
        user.id,
        session,
        "remove host",
        [MemberRole.OWNER, MemberRole.ADMIN],
    )

    query = select(HostDevice).where(
        HostDevice.org_id == organization_id, HostDevice.id == host_id
    )
    result = await session.execute(query)
    host_device = result.scalar_one_or_none()

    if not host_device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Host not found"
        )

    await session.delete(host_device)
    await session.commit()

    return {"message": "Host deleted successfully."}
