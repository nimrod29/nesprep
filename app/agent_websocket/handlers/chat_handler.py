"""Chat handler: orchestrate history, events, and agent dispatch for chat-based planning."""

import logging

from fastapi import WebSocket
from langchain_core.messages import AIMessage, HumanMessage

from app.agent_websocket.consts.events import EventTypes
from app.agent_websocket.events.event_emitter import emit_event
from app.agents.planning_chat_agent import PlanningChatAgent
from app.dal import get_session
from app.dal.models import MessageRole, PlanningMessage

logger = logging.getLogger(__name__)

CHAT_HISTORY_LIMIT = 30


def convert_messages_to_langchain(
    messages: list[PlanningMessage],
) -> list[HumanMessage | AIMessage]:
    """Convert PlanningMessage records to LangChain message objects."""
    result: list[HumanMessage | AIMessage] = []
    for msg in messages:
        if msg.role == MessageRole.user:
            result.append(HumanMessage(content=msg.content))
        elif msg.role == MessageRole.assistant:
            result.append(AIMessage(content=msg.content))
    return result


async def handle_chat_send(
    websocket: WebSocket,
    shift_plan_id: int,
    message: str,
    manager_id: int,
    connection_state: dict | None = None,
) -> None:
    """Handle chat.send: load history, save user message, run agent, emit events.

    Args:
        websocket: The WebSocket connection.
        shift_plan_id: The shift plan ID (acts as session ID).
        message: The user's message.
        manager_id: The manager ID.
        connection_state: Shared state for the connection.
    """
    connection_state = connection_state or {}

    db = get_session()
    try:
        messages = PlanningMessage.get_recent_by_shift_plan(
            db, shift_plan_id, limit=CHAT_HISTORY_LIMIT
        )
        chat_history = convert_messages_to_langchain(messages)

        PlanningMessage.create(
            db,
            shift_plan_id=shift_plan_id,
            role=MessageRole.user,
            content=message,
        )
    finally:
        db.close()

    await emit_event(
        websocket,
        str(shift_plan_id),
        EventTypes.CHAT_STARTED,
        {},
    )

    async def status_callback(text: str) -> None:
        await emit_event(
            websocket,
            str(shift_plan_id),
            EventTypes.STATUS_UPDATE,
            {"message": text},
        )

    async def plan_callback(week_plans: list[dict]) -> None:
        await emit_event(
            websocket,
            str(shift_plan_id),
            EventTypes.PLAN_COMPLETED,
            {"week_plans": week_plans},
        )

    try:
        agent = PlanningChatAgent(
            shift_plan_id=shift_plan_id,
            manager_id=manager_id,
            status_callback=status_callback,
            plan_callback=plan_callback,
        )

        response = await agent.run(message, chat_history)

        db = get_session()
        try:
            PlanningMessage.create(
                db,
                shift_plan_id=shift_plan_id,
                role=MessageRole.assistant,
                content=response or "",
            )
        finally:
            db.close()

        await emit_event(
            websocket,
            str(shift_plan_id),
            EventTypes.CHAT_COMPLETED,
            {"response": response or ""},
        )

    except Exception as e:
        logger.exception("Agent error in shift plan %s", shift_plan_id)

        db = get_session()
        try:
            PlanningMessage.create(
                db,
                shift_plan_id=shift_plan_id,
                role=MessageRole.assistant,
                content=f"Error: {e}",
            )
        finally:
            db.close()

        await emit_event(
            websocket,
            str(shift_plan_id),
            EventTypes.ERROR,
            {"code": "agent_error", "message": str(e)},
        )
        await emit_event(
            websocket,
            str(shift_plan_id),
            EventTypes.CHAT_COMPLETED,
            {"response": "", "error": True},
        )
