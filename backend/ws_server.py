"""
Desktop AI Lifeform — WebSocket Server (ws_server.py)
======================================================
Broadcasts creature state to the Godot frontend over a local
WebSocket connection. Handles multiple clients gracefully
(e.g., reconnections after Godot restarts).
"""

import asyncio
import json
import logging
from datetime import datetime, timezone
from typing import Set

import websockets
from websockets.server import WebSocketServerProtocol

from backend import config

logger = logging.getLogger(__name__)


class WSServer:
    """
    Local WebSocket server. Godot connects here.
    Broadcasts JSON messages to all connected clients.
    """

    def __init__(self):
        self._clients: Set[WebSocketServerProtocol] = set()
        self._server = None

    async def start(self):
        """Start the WebSocket server and keep it running."""
        self._server = await websockets.serve(
            self._handle_client,
            config.WS_HOST,
            config.WS_PORT,
            ping_interval=20,
            ping_timeout=30,
        )
        logger.info(f"WebSocket server listening on ws://{config.WS_HOST}:{config.WS_PORT}")

    async def stop(self):
        if self._server:
            self._server.close()
            await self._server.wait_closed()

    async def _handle_client(self, ws: WebSocketServerProtocol):
        """Manage a single client connection."""
        self._clients.add(ws)
        addr = ws.remote_address
        logger.info(f"Client connected: {addr} (total: {len(self._clients)})")

        try:
            async for raw in ws:
                await self._handle_message(ws, raw)
        except websockets.exceptions.ConnectionClosedError:
            pass
        finally:
            self._clients.discard(ws)
            logger.info(f"Client disconnected: {addr} (total: {len(self._clients)})")

    async def _handle_message(self, ws: WebSocketServerProtocol, raw: str):
        """Handle incoming messages from the frontend."""
        try:
            msg = json.loads(raw)
        except json.JSONDecodeError:
            return

        if msg.get("type") == "ping":
            await ws.send(json.dumps({"type": "pong"}))

    async def broadcast(self, payload: dict):
        """Send a JSON message to all connected clients."""
        if not self._clients:
            return
        payload["timestamp"] = datetime.now(timezone.utc).isoformat()
        message = json.dumps(payload)
        # Send concurrently to all clients; swallow individual send errors
        results = await asyncio.gather(
            *[client.send(message) for client in list(self._clients)],
            return_exceptions=True,
        )
        for r in results:
            if isinstance(r, Exception):
                logger.debug(f"Broadcast send error: {r}")

    async def broadcast_state(self, state_dict: dict):
        """Convenience method: broadcast a state_update message."""
        await self.broadcast({"type": "state_update", **state_dict})

    async def broadcast_thought(self, text: str, duration_ms: int = 4000):
        """Broadcast an LLM-generated ambient thought."""
        await self.broadcast({
            "type": "thought",
            "text": text,
            "duration_ms": duration_ms,
        })

    async def broadcast_stimulus(self, event: str, intensity: float):
        """Broadcast a direct stimulus event for immediate reaction."""
        await self.broadcast({
            "type": "stimulus",
            "event": event,
            "intensity": round(intensity, 3),
        })

    @property
    def client_count(self) -> int:
        return len(self._clients)
