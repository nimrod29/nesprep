"""WebSocket endpoint and message routing for chat-based planning."""

import logging
from datetime import date

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.agent_websocket.consts.events import EventTypes
from app.agent_websocket.consts.messages import ClientMessageTypes
from app.agent_websocket.events.event_emitter import emit_event
from app.agent_websocket.handlers.chat_handler import handle_chat_send

logger = logging.getLogger(__name__)

router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    """Accept WebSocket connection and route messages by type.

    The main interaction is through chat.send, which routes to the
    PlanningChatAgent for conversational shift planning.
    """
    await websocket.accept()

    connection_state: dict = {
        "manager_id": None,
        "current_shift_plan_id": None,
    }

    try:
        while True:
            data = await websocket.receive_json()
            msg_type = data.get("type")
            session_id = data.get("session_id", "")

            if msg_type == ClientMessageTypes.AUTH_SET_TOKEN:
                manager_id = data.get("manager_id")
                if manager_id:
                    connection_state["manager_id"] = manager_id
                    logger.info("Manager %s connected", manager_id)
                else:
                    logger.warning("Received auth.set_token without manager_id")

            elif msg_type == ClientMessageTypes.SESSION_JOIN:
                shift_plan_id = data.get("shift_plan_id")

                if shift_plan_id:
                    connection_state["current_shift_plan_id"] = shift_plan_id
                    await emit_event(
                        websocket,
                        session_id,
                        EventTypes.SESSION_JOINED,
                        {"shift_plan_id": shift_plan_id},
                    )
                else:
                    manager_id = connection_state.get("manager_id")
                    if not manager_id:
                        await emit_event(
                            websocket,
                            session_id,
                            EventTypes.ERROR,
                            {"code": "not_authenticated", "message": "Manager ID not set"},
                        )
                        continue

                    week_start_str = data.get("week_start")
                    template_path = data.get("template_path")
                    title = data.get("title")

                    week_start = None
                    if week_start_str:
                        try:
                            week_start = date.fromisoformat(week_start_str)
                        except ValueError:
                            await emit_event(
                                websocket,
                                session_id,
                                EventTypes.ERROR,
                                {"code": "invalid_date", "message": "Invalid week_start format"},
                            )
                            continue

                    from app.dal import get_session
                    from app.dal.models import ShiftPlan

                    db = get_session()
                    try:
                        shift_plan = ShiftPlan.create(
                            db,
                            manager_id=manager_id,
                            week_start=week_start or date.today(),
                            title=title,
                            template_path=template_path,
                        )
                        connection_state["current_shift_plan_id"] = shift_plan.id

                        await emit_event(
                            websocket,
                            session_id,
                            EventTypes.SESSION_JOINED,
                            {
                                "shift_plan_id": shift_plan.id,
                                "week_start": (week_start or date.today()).isoformat(),
                                "title": title,
                                "new": True,
                            },
                        )
                    finally:
                        db.close()

            elif msg_type == ClientMessageTypes.CHAT_SEND:
                shift_plan_id = connection_state.get("current_shift_plan_id")
                manager_id = connection_state.get("manager_id")

                if not manager_id:
                    await emit_event(
                        websocket,
                        session_id,
                        EventTypes.ERROR,
                        {"code": "not_authenticated", "message": "Manager ID not set"},
                    )
                    continue

                if not shift_plan_id:
                    await emit_event(
                        websocket,
                        session_id,
                        EventTypes.ERROR,
                        {"code": "no_session", "message": "No active shift plan session"},
                    )
                    continue

                message = data.get("message", "")
                if not message:
                    await emit_event(
                        websocket,
                        session_id,
                        EventTypes.ERROR,
                        {"code": "empty_message", "message": "Message cannot be empty"},
                    )
                    continue

                await handle_chat_send(
                    websocket=websocket,
                    shift_plan_id=shift_plan_id,
                    message=message,
                    manager_id=manager_id,
                    connection_state=connection_state,
                )

            else:
                await emit_event(
                    websocket,
                    session_id,
                    EventTypes.ERROR,
                    {"code": "unknown_message", "message": f"Unknown type: {msg_type}"},
                )

    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
