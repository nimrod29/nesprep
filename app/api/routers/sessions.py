"""Sessions API endpoints for shift plan management."""

from datetime import date

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from app.dal import get_session
from app.dal.models import MessageRole, PlanningMessage, PlanStatus, ShiftPlan

router = APIRouter(prefix="/sessions", tags=["sessions"])


class SessionCreate(BaseModel):
    """Request body for creating a new session."""

    manager_id: int
    title: str | None = None
    week_start: date | None = None


class SessionResponse(BaseModel):
    """Response body for a session."""

    id: int
    manager_id: int
    title: str | None
    week_start: date
    status: str
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class SessionListResponse(BaseModel):
    """Response body for session list."""

    sessions: list[SessionResponse]


class MessageResponse(BaseModel):
    """Response body for a chat message."""

    id: int
    role: str
    content: str
    created_at: str

    class Config:
        from_attributes = True


class MessagesListResponse(BaseModel):
    """Response body for messages list."""

    messages: list[MessageResponse]


def _get_status_value(status: PlanStatus | str) -> str:
    """Extract status value from PlanStatus enum or string."""
    return status.value if isinstance(status, PlanStatus) else status


def _build_session_response(sp: ShiftPlan) -> SessionResponse:
    """Build a SessionResponse from a ShiftPlan, handling None values."""
    updated_at = sp.updated_at or sp.created_at
    return SessionResponse(
        id=sp.id,
        manager_id=sp.manager_id,
        title=sp.title,
        week_start=sp.week_start,
        status=_get_status_value(sp.status),
        created_at=sp.created_at.isoformat(),
        updated_at=updated_at.isoformat(),
    )


@router.get("", response_model=SessionListResponse)
def list_sessions(manager_id: int = Query(..., description="Manager ID")) -> SessionListResponse:
    """List all shift plans for a manager."""
    db = get_session()
    try:
        shift_plans = ShiftPlan.get_by_manager(db, manager_id)
        sessions = [_build_session_response(sp) for sp in shift_plans]
        return SessionListResponse(sessions=sessions)
    finally:
        db.close()


@router.post("", response_model=SessionResponse)
def create_session(request: SessionCreate) -> SessionResponse:
    """Create a new shift plan session."""
    db = get_session()
    try:
        shift_plan = ShiftPlan.create(
            db,
            manager_id=request.manager_id,
            title=request.title,
            week_start=request.week_start or date.today(),
        )
        return _build_session_response(shift_plan)
    finally:
        db.close()


@router.get("/{session_id}", response_model=SessionResponse)
def get_session_by_id(session_id: int) -> SessionResponse:
    """Get a specific shift plan session."""
    db = get_session()
    try:
        shift_plan = ShiftPlan.get_by_id(db, session_id)
        if not shift_plan:
            raise HTTPException(status_code=404, detail="Session not found")

        return _build_session_response(shift_plan)
    finally:
        db.close()


@router.delete("/{session_id}")
def delete_session(session_id: int) -> dict:
    """Delete a shift plan session."""
    db = get_session()
    try:
        shift_plan = ShiftPlan.get_by_id(db, session_id)
        if not shift_plan:
            raise HTTPException(status_code=404, detail="Session not found")

        db.delete(shift_plan)
        db.commit()
        return {"deleted": True, "id": session_id}
    finally:
        db.close()


@router.get("/{session_id}/messages", response_model=MessagesListResponse)
def get_session_messages(session_id: int) -> MessagesListResponse:
    """Get all messages for a shift plan session."""
    db = get_session()
    try:
        shift_plan = ShiftPlan.get_by_id(db, session_id)
        if not shift_plan:
            raise HTTPException(status_code=404, detail="Session not found")

        planning_messages = PlanningMessage.get_by_shift_plan(db, session_id)
        messages = [
            MessageResponse(
                id=msg.id,
                role=msg.role.value if isinstance(msg.role, MessageRole) else msg.role,
                content=msg.content,
                created_at=msg.created_at.isoformat(),
            )
            for msg in planning_messages
        ]
        return MessagesListResponse(messages=messages)
    finally:
        db.close()
