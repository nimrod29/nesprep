"""PlanningMessage model."""

import enum

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, Text
from sqlalchemy.orm import Session, relationship
from sqlalchemy.sql import func

from app.dal.base import Base


class MessageRole(enum.Enum):
    """Message role enum."""

    user = "user"
    assistant = "assistant"
    system = "system"
    tool = "tool"


class PlanningMessage(Base):
    """PlanningMessage model - chat history within a shift plan."""

    __tablename__ = "planning_messages"

    id = Column(Integer, primary_key=True, index=True)
    shift_plan_id = Column(Integer, ForeignKey("shift_plans.id"), nullable=False, index=True)
    role = Column(Enum(MessageRole), nullable=False)
    content = Column(Text, nullable=False)
    tool_calls_json = Column(Text, nullable=True)
    tool_call_id = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    shift_plan = relationship("ShiftPlan", back_populates="messages")

    @staticmethod
    def create(
        db: Session,
        shift_plan_id: int,
        role: MessageRole,
        content: str,
        tool_calls_json: str | None = None,
        tool_call_id: str | None = None,
    ) -> "PlanningMessage":
        """Create a new planning message."""
        message = PlanningMessage(
            shift_plan_id=shift_plan_id,
            role=role,
            content=content,
            tool_calls_json=tool_calls_json,
            tool_call_id=tool_call_id,
        )
        db.add(message)
        db.commit()
        db.refresh(message)
        return message

    @staticmethod
    def get_by_shift_plan(
        db: Session, shift_plan_id: int, limit: int | None = None
    ) -> list["PlanningMessage"]:
        """Get all messages for a shift plan, ordered by creation time."""
        query = (
            db.query(PlanningMessage)
            .filter(PlanningMessage.shift_plan_id == shift_plan_id)
            .order_by(PlanningMessage.created_at.asc())
        )
        if limit:
            query = query.limit(limit)
        return query.all()

    @staticmethod
    def get_recent_by_shift_plan(
        db: Session, shift_plan_id: int, limit: int = 30
    ) -> list["PlanningMessage"]:
        """Get the most recent N messages for a shift plan, in chronological order."""
        messages = (
            db.query(PlanningMessage)
            .filter(PlanningMessage.shift_plan_id == shift_plan_id)
            .order_by(PlanningMessage.created_at.desc())
            .limit(limit)
            .all()
        )
        return list(reversed(messages))
