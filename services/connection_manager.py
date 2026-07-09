import asyncio
import logging
from fastapi import WebSocket

logger = logging.getLogger(__name__)


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}
        self.pending_responses: dict[str, asyncio.Future] = {}

    def connect(self, host_id: str, websocket: WebSocket):
        self.active_connections[host_id] = websocket
        logger.info(f"Host {host_id} connected. Total connections")

    def disconnect(self, host_id: str):
        if host_id in self.active_connections:
            del self.active_connections[host_id]
            logger.info(f"Host {host_id} disconnected.")

    async def send_and_wait(
        self, host_id: str, message_id: str, payload: dict, timeout: int = 30
    ) -> dict:
        ws = self.active_connections.get(host_id)
        if not ws:
            return {"error": f"host {host_id} is offline."}

        future = asyncio.get_running_loop().create_future()
        self.pending_responses[message_id] = future

        try:
            await ws.send_json(payload)

            result = await asyncio.wait_for(future, timeout)
            return result
        except asyncio.TimeoutError:
            return {"error": "Tool execution timed out."}
        finally:
            self.pending_responses.pop(message_id, None)

    def route_response(self, message_id: str, payload: dict):
        if message_id in self.pending_responses:
            self.pending_responses[message_id].set_result(payload)


conn_manager = ConnectionManager()
