import logging
import secrets
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from supabase_auth import User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from haikunator import Haikunator

from main import get_session
from clients.supabase_client import get_current_user
from utils.permission import verify_permission
from models.model import AuthToken, MemberRole
from schemas.token import (
    CreateTokenRequest,
    UpdateTokenNameRequest,
    UpdateTokenStatusRequest,
    TokenResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter()

haiku = Haikunator()


@router.get("/{organization_id}/tokens", response_model=list[TokenResponse])
async def get_auth_tokens(
    organization_id: UUID,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    try:
        await verify_permission(
            organization_id,
            user.id,
            session,
            "view auth tokens",
            [MemberRole.OWNER, MemberRole.ADMIN],
        )

        query = select(AuthToken).where(AuthToken.org_id == organization_id)
        result = await session.execute(query)
        tokens = result.scalars().all()

        return [TokenResponse.model_validate(token) for token in tokens]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching auth tokens: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.post("/{organization_id}/tokens")
async def create_auth_token(
    organization_id: UUID,
    payload: CreateTokenRequest,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    try:
        await verify_permission(
            organization_id,
            user.id,
            session,
            "create auth token",
            [MemberRole.OWNER, MemberRole.ADMIN],
        )

        token_name = payload.name if payload.name else haiku.haikunate()
        raw_token = f"n2h_{secrets.token_urlsafe(32)}"

        new_auth_token = AuthToken(
            org_id=organization_id,
            name=token_name,
            token=raw_token,
            created_by=user.id,
            is_active=True,
            expires_at=payload.expires_at,
        )

        session.add(new_auth_token)
        await session.commit()

        return {
            "name": token_name,
            "token": raw_token,
            "message": "Token created successfully",
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating auth token: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.patch("/{organization_id}/tokens/{token_id}/name")
async def update_auth_token(
    organization_id: UUID,
    token_id: UUID,
    payload: UpdateTokenNameRequest,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    try:
        await verify_permission(
            organization_id,
            user.id,
            session,
            "update auth token",
            [MemberRole.OWNER, MemberRole.ADMIN],
        )

        query = select(AuthToken).where(
            AuthToken.org_id == organization_id, AuthToken.id == token_id
        )
        result = await session.execute(query)
        auth_token = result.scalar_one_or_none()

        if not auth_token:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Auth token not found."
            )

        auth_token.name = payload.name if payload.name else auth_token.name

        session.add(auth_token)
        await session.commit()
        await session.refresh(auth_token)

        return {
            "id": str(auth_token.id),
            "name": auth_token.name,
            "message": "Auth token updated successfully.",
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating auth token: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.patch("/{organization_id}/tokens/{token_id}/status")
async def update_auth_token_status(
    organization_id: UUID,
    token_id: UUID,
    payload: UpdateTokenStatusRequest,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    try:
        await verify_permission(
            organization_id,
            user.id,
            session,
            "update auth token status",
            [MemberRole.OWNER, MemberRole.ADMIN],
        )

        query = select(AuthToken).where(
            AuthToken.org_id == organization_id, AuthToken.id == token_id
        )
        result = await session.execute(query)
        auth_token = result.scalar_one_or_none()

        if not auth_token:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Auth token not found."
            )

        auth_token.is_active = payload.is_active

        session.add(auth_token)
        await session.commit()
        await session.refresh(auth_token)

        return {
            "id": str(auth_token.id),
            "is_active": auth_token.is_active,
            "message": f"Auth token { 'activated' if payload.is_active else 'deactivated' } successfully.",
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating auth token status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.delete("/{organization_id}/tokens/{token_id}")
async def delete_auth_token(
    organization_id: UUID,
    token_id: UUID,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    try:
        await verify_permission(
            organization_id,
            user.id,
            session,
            "delete auth token",
            [MemberRole.OWNER, MemberRole.ADMIN],
        )

        query = select(AuthToken).where(
            AuthToken.org_id == organization_id, AuthToken.id == token_id
        )
        result = await session.execute(query)
        auth_token = result.scalar_one_or_none()

        if not auth_token:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Auth token not found."
            )

        await session.delete(auth_token)
        await session.commit()

        return {"message": "Auth token deleted successfully."}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting auth token: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )
