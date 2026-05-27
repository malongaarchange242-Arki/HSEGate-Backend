"""WebSocket endpoints for real-time updates."""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.websocket.manager import manager
from app.core.security import decode_token
import json

router = APIRouter()


@router.websocket("/ws/{token}")
async def websocket_endpoint(websocket: WebSocket, token: str):
    """
    WebSocket endpoint for real-time updates.
    
    Connect with: ws://localhost:8000/api/v1/ws/{jwt_token}
    
    Messages format:
    {
        "type": "incident|alert|detection",
        "channel": "default|zone_a|zone_b",
        "data": {...}
    }
    """
    # Verify JWT token
    payload = decode_token(token)
    if not payload:
        await websocket.close(code=1008, reason="Invalid token")
        return

    user_id = payload.get("sub")
    if not user_id:
        await websocket.close(code=1008, reason="Invalid token")
        return

    # Connect to default channel
    await manager.connect(websocket, channel="default")

    try:
        while True:
            data = await websocket.receive_json()

            # Handle different message types
            if data.get("type") == "ping":
                await manager.send_personal(
                    websocket,
                    {"type": "pong", "timestamp": str(__import__('datetime').datetime.utcnow())},
                )

            elif data.get("type") == "subscribe":
                # Subscribe to a channel
                channel = data.get("channel", "default")
                old_channel = manager.user_channels.get(id(websocket), "default")
                if old_channel in manager.active_connections:
                    manager.active_connections[old_channel].discard(websocket)
                if channel not in manager.active_connections:
                    manager.active_connections[channel] = set()
                manager.active_connections[channel].add(websocket)
                manager.user_channels[id(websocket)] = channel

                await manager.send_personal(
                    websocket,
                    {"type": "subscribed", "channel": channel},
                )

            elif data.get("type") == "unsubscribe":
                # Unsubscribe from a channel
                await manager.disconnect(websocket)

            else:
                # Echo back unknown messages
                await manager.send_personal(
                    websocket,
                    {"type": "echo", "data": data},
                )

    except WebSocketDisconnect:
        await manager.disconnect(websocket)
        print(f"Client disconnected")


@router.websocket("/ws/monitoring/{token}")
async def websocket_monitoring_endpoint(websocket: WebSocket, token: str):
    """
    WebSocket endpoint for monitoring dashboard.
    
    Connect with: ws://localhost:8000/api/v1/ws/monitoring/{jwt_token}
    
    Receives live incidents, alerts, and detections.
    """
    # Verify JWT token
    payload = decode_token(token)
    if not payload:
        await websocket.close(code=1008, reason="Invalid token")
        return

    user_id = payload.get("sub")
    if not user_id:
        await websocket.close(code=1008, reason="Invalid token")
        return

    # Connect to monitoring channel
    await manager.connect(websocket, channel="monitoring")

    try:
        # Send initial stats
        stats = manager.get_stats()
        await manager.send_personal(websocket, {"type": "stats", "data": stats})

        while True:
            # Keep connection alive and wait for commands
            data = await websocket.receive_json()

            if data.get("type") == "ping":
                stats = manager.get_stats()
                await manager.send_personal(
                    websocket,
                    {"type": "pong", "data": stats},
                )

    except WebSocketDisconnect:
        await manager.disconnect(websocket)


@router.get("/ws/stats")
async def get_websocket_stats():
    """
    Get WebSocket connection statistics.
    
    Returns connection count and channel information.
    """
    return manager.get_stats()
