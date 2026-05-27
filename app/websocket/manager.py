"""WebSocket connection manager for real-time updates."""

from fastapi import WebSocket
from typing import Dict, Set
from datetime import datetime
import json


class ConnectionManager:
    """Manage WebSocket connections and broadcast messages."""

    def __init__(self):
        """Initialize connection manager."""
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        self.user_channels: Dict[str, str] = {}

    async def connect(self, websocket: WebSocket, channel: str = "default"):
        """
        Accept a WebSocket connection and add it to a channel.
        
        - **websocket**: WebSocket connection
        - **channel**: Channel name (default: "default")
        """
        await websocket.accept()

        if channel not in self.active_connections:
            self.active_connections[channel] = set()

        self.active_connections[channel].add(websocket)
        self.user_channels[id(websocket)] = channel

        print(f"✅ Client connected to {channel}. Active: {len(self.active_connections[channel])}")

    async def disconnect(self, websocket: WebSocket):
        """
        Disconnect a WebSocket and remove from channel.
        
        - **websocket**: WebSocket connection
        """
        channel = self.user_channels.pop(id(websocket), "default")

        if channel in self.active_connections:
            self.active_connections[channel].discard(websocket)

            if not self.active_connections[channel]:
                del self.active_connections[channel]

        print(f"❌ Client disconnected from {channel}")

    async def broadcast_to_channel(self, message: dict, channel: str = "default"):
        """
        Broadcast message to all clients in a channel.
        
        - **message**: Message dict to broadcast
        - **channel**: Channel name
        """
        if channel not in self.active_connections:
            return

        disconnected_clients = set()

        for connection in self.active_connections[channel]:
            try:
                await connection.send_json(message)
            except Exception as e:
                print(f"❌ Error sending message: {e}")
                disconnected_clients.add(connection)

        # Clean up disconnected clients
        for connection in disconnected_clients:
            await self.disconnect(connection)

    async def broadcast_to_all(self, message: dict):
        """
        Broadcast message to all connected clients across all channels.
        
        - **message**: Message dict to broadcast
        """
        for channel in self.active_connections:
            await self.broadcast_to_channel(message, channel)

    async def send_personal(self, websocket: WebSocket, message: dict):
        """
        Send message to a specific client.
        
        - **websocket**: WebSocket connection
        - **message**: Message dict
        """
        try:
            await websocket.send_json(message)
        except Exception as e:
            print(f"❌ Error sending personal message: {e}")
            await self.disconnect(websocket)

    async def broadcast_incident(self, incident_data: dict):
        """
        Broadcast incident event to all clients.
        
        - **incident_data**: Incident data
        """
        message = {
            "type": "incident",
            "timestamp": datetime.utcnow().isoformat(),
            "data": incident_data,
        }
        await self.broadcast_to_all(message)

    async def broadcast_alert(self, alert_data: dict):
        """
        Broadcast alert event to all clients.
        
        - **alert_data**: Alert data
        """
        message = {
            "type": "alert",
            "timestamp": datetime.utcnow().isoformat(),
            "data": alert_data,
        }
        await self.broadcast_to_all(message)

    async def broadcast_detection(self, detection_data: dict):
        """
        Broadcast detection event to all clients.
        
        - **detection_data**: Detection data
        """
        message = {
            "type": "detection",
            "timestamp": datetime.utcnow().isoformat(),
            "data": detection_data,
        }
        await self.broadcast_to_all(message)

    def get_stats(self) -> dict:
        """Get connection statistics."""
        total_clients = sum(len(clients) for clients in self.active_connections.values())
        return {
            "total_clients": total_clients,
            "channels": list(self.active_connections.keys()),
            "clients_per_channel": {
                channel: len(clients)
                for channel, clients in self.active_connections.items()
            },
        }


# Global connection manager instance
manager = ConnectionManager()
