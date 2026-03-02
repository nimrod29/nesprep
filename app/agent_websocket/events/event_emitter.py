"""Emit JSON events to the WebSocket client."""

import time
from typing import Any

from fastapi import WebSocket


async def emit_event(
    websocket: WebSocket,
    session_id: int | str,
    event_type: str,
    payload: dict[str, Any],
) -> None:
    """Send a JSON event envelope to the client."""
    await websocket.send_json(
        {
            "session_id": session_id,
            "type": event_type,
            "ts": int(time.time() * 1000),
            "payload": payload,
        }
    )
