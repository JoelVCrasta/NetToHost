import asyncio
import logging
from typing import Any, Union
from fastapi import WebSocket
from uuid import uuid4

from schemas.protocol import (
    ActionType,
    ExecuteToolRequest,
    GetToolsRequest,
    GetToolsResponse,
)

logger = logging.getLogger(__name__)


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}
        self.pending_responses: dict[str, asyncio.Future] = {}
        self.available_tools: dict[str, list[dict[str, Any]]] = {}

    def connect(self, host_id: str, websocket: WebSocket):
        self.active_connections[host_id] = websocket
        logger.info(f"Host {host_id} connected. Total connections")

    def disconnect(self, host_id: str):
        if host_id in self.active_connections:
            del self.active_connections[host_id]
        self.available_tools.pop(host_id, None)
        logger.info(f"Host {host_id} disconnected.")

    async def sync_host_tools(self, host_id: str) -> bool:
        """Request the list of available tools from the host during the initial connection."""
        message_id = str(uuid4())
        payload = GetToolsRequest(action=ActionType.GET_TOOLS, message_id=message_id)

        logger.info(f"Syncing tools with the host {host_id}...")
        response = await self.send_and_wait(host_id, message_id, payload)

        if "error" in response:
            logger.error(
                f"Failed to sync tools with host {host_id}: {response['error']}"
            )
            return False

        try:
            validated_response = GetToolsResponse.model_validate(response)
            if validated_response.error:
                logger.error(
                    f"Error from host {host_id} while syncing tools: {validated_response.error}"
                )
                return False

            self.available_tools[host_id] = validated_response.result
            logger.info(f"Successfully synced tools with host {host_id}.")
            return True
        except Exception as e:
            logger.error(f"Failed to validate tools response from host {host_id}: {e}")
            return False

    async def send_and_wait(
        self,
        host_id: str,
        message_id: str,
        payload: Union[GetToolsRequest, ExecuteToolRequest],
        timeout: int = 30,
    ) -> dict:
        """Send a message to the host and wait for a response."""
        ws = self.active_connections.get(host_id)
        if not ws:
            return {"error": f"host {host_id} is offline."}

        future = asyncio.get_running_loop().create_future()
        self.pending_responses[message_id] = future

        try:
            data = payload.model_dump() if hasattr(payload, "model_dump") else payload
            await ws.send_json(data)

            result = await asyncio.wait_for(future, timeout)
            return result
        except asyncio.TimeoutError:
            return {"error": "Tool execution timed out."}
        finally:
            self.pending_responses.pop(message_id, None)

    def route_response(self, message_id: str, payload: dict):
        """Update the pending response for a given message_id with the received payload."""
        if message_id in self.pending_responses:
            self.pending_responses[message_id].set_result(payload)


conn_manager = ConnectionManager()
