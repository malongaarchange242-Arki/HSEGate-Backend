"""WebSocket manager for real-time communications."""

from typing import Set
from fastapi import WebSocket
import json
import logging

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manage WebSocket connections and broadcast messages."""

    def __init__(self):
        self.active_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket):
        """Accept a new WebSocket connection."""
        await websocket.accept()
        self.active_connections.add(websocket)
        logger.info(f"Client connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        """Remove a disconnected WebSocket."""
        self.active_connections.discard(websocket)
        logger.info(f"Client disconnected. Total connections: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        """Send a message to all connected clients."""
        if not self.active_connections:
            return
        
        message_json = json.dumps(message)
        disconnected = set()
        
        for connection in self.active_connections:
            try:
                await connection.send_text(message_json)
            except Exception as e:
                logger.error(f"Error sending message: {e}")
                disconnected.add(connection)
        
        # Remove disconnected clients
        self.active_connections -= disconnected

    async def broadcast_to_role(self, message: dict, roles: list):
        """Send a message to clients with specific roles."""
        # For Phase 2 - will implement role-based broadcasting
        await self.broadcast(message)


manager = ConnectionManager()
