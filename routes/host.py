import logging
import secrets
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from supabase_auth import User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from main import get_session
from auth.supabase_client import get_current_user
from utils.permission import verify_permission
from models.model import HostDevice, MemberRole

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/{organization_id}/hosts")
async def get_hosts(
    organization_id: UUID,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    try:
        query = select(HostDevice).where(HostDevice.org_id == organization_id)
        result = await session.execute(query)
        hosts = result.scalars().all()

        return hosts
    except Exception as e:
        logger.error(f"Error fetching hosts: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )

