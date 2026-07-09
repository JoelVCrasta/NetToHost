import logging
import json
import asyncio
from uuid import UUID
from fastapi import (
    APIRouter,
    WebSocket,
    WebSocketDisconnect,
    Depends,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from datetime import datetime, timezone
from haikunator import Haikunator

from main import get_session
from clients.redis_client import redis
from models.model import AuthToken, HostDevice
from services.connection_manager import conn_manager

logger = logging.getLogger(__name__)

router = APIRouter()

haiku = Haikunator()


@router.websocket("/ws/agent")
async def agent_tunnel(
    websocket: WebSocket,
    token: str,
    host_id: str,
    session: AsyncSession = Depends(get_session),
):
    await websocket.accept()

    token_query = select(AuthToken).where(
        AuthToken.token == token, AuthToken.is_active == True
    )
    result = await session.execute(token_query)
    auth_token = result.scalar_one_or_none()

    if not auth_token:
        await websocket.close(
            code=status.WS_1008_POLICY_VIOLATION, reason="Invalid or inactive token"
        )
        return

    if auth_token.expires_at and auth_token.expires_at < datetime.now(timezone.utc):
        await websocket.close(
            code=status.WS_1008_POLICY_VIOLATION, reason="Token has expired"
        )
        return

    host_query = select(HostDevice).where(
        HostDevice.host_id == host_id, HostDevice.org_id == auth_token.org_id
    )
    result = await session.execute(host_query)
    host = result.scalar_one_or_none()

    if host:
        host.is_online = True
        host.last_seen = datetime.now(timezone.utc)
    else:
        host = HostDevice(
            host_id=host_id,
            org_id=auth_token.org_id,
            name=haiku.haikunate(token_length=2),
            is_online=True,
            last_seen=datetime.now(timezone.utc),
        )

    session.add(host)
    await session.commit()
    await session.refresh(host)

    conn_manager.connect(host_id, websocket)

    pubsub = redis.pubsub()
    await pubsub.subscribe(f"host:{host_id}")

    try:

        async def redis_listener():
            async for message in pubsub.listen():
                if message["type"] == "message":
                    await websocket.send_text(message["data"])

        listener_task = asyncio.create_task(redis_listener())

        while True:
            data = await websocket.receive_text()
            logger.info(f"Received data from host {host_id}: {data}")

            try:
                payload = json.loads(data)
                if "message_id" in payload:
                    conn_manager.route_response(payload["message_id"], payload)
            except json.JSONDecodeError:
                logger.error(f"Invalid JSON received from host {host_id}: {data}")

    except WebSocketDisconnect:
        logger.info(f"Host {host_id} disconnected")

    except Exception as e:
        logger.error(f"Error in WebSocket connection for host {host_id}: {e}")
        try:
            await websocket.close(
                code=status.WS_1011_INTERNAL_ERROR, reason="Internal server error"
            )
        except RuntimeError:
            pass
    finally:
        conn_manager.disconnect(host_id)
        
        listener_task.cancel()
        await pubsub.unsubscribe(f"host:{host_id}")
        await pubsub.close()

        try:
            host.is_online = False
            host.last_seen = datetime.now(timezone.utc)
            session.add(host)
            await session.commit()
        except Exception as e:
            logger.error(f"Error updating host status on disconnect: {e}")
