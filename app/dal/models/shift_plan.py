"""ShiftPlan model."""

import enum
import json

from sqlalchemy import Column, Date, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Session, relationship
from sqlalchemy.sql import func

from app.dal.base import Base


class PlanStatus(enum.Enum):
    """Status of a shift plan."""

    draft = "draft"
    analyzing = "analyzing"
    planning = "planning"
    validating = "validating"
    completed = "completed"
    failed = "failed"


class ShiftPlan(Base):
    """ShiftPlan model - a planning session for a specific week."""

    __tablename__ = "shift_plans"

    id = Column(Integer, primary_key=True, index=True)
    manager_id = Column(Integer, ForeignKey("managers.id"), nullable=False, index=True)
    title = Column(String(255), nullable=True)
    week_start = Column(Date, nullable=False)
    status = Column(Enum(PlanStatus), default=PlanStatus.draft)
    template_path = Column(String(500), nullable=True)
    output_path = Column(String(500), nullable=True)
    plan_json = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    manager = relationship("Manager", back_populates="shift_plans")
    messages = relationship(
        "PlanningMessage",
        back_populates="shift_plan",
        cascade="all, delete-orphan",
        order_by="PlanningMessage.created_at",
    )
    constraints = relationship(
        "EmployeeConstraint", back_populates="shift_plan", cascade="all, delete-orphan"
    )

    @staticmethod
    def create(
        db: Session,
        manager_id: int,
        week_start,
        title: str | None = None,
        template_path: str | None = None,
    ) -> "ShiftPlan":
        """Create a new shift plan."""
        shift_plan = ShiftPlan(
            manager_id=manager_id,
            week_start=week_start,
            title=title,
            template_path=template_path,
        )
        db.add(shift_plan)
        db.commit()
        db.refresh(shift_plan)
        return shift_plan

    @staticmethod
    def get_by_id(db: Session, shift_plan_id: int) -> "ShiftPlan | None":
        """Get shift plan by ID."""
        return db.query(ShiftPlan).filter(ShiftPlan.id == shift_plan_id).first()

    @staticmethod
    def get_by_manager(db: Session, manager_id: int, limit: int = 50) -> list["ShiftPlan"]:
        """Get all shift plans for a manager, ordered by most recent."""
        return (
            db.query(ShiftPlan)
            .filter(ShiftPlan.manager_id == manager_id)
            .order_by(ShiftPlan.created_at.desc())
            .limit(limit)
            .all()
        )

    def update_status(self, db: Session, status: PlanStatus) -> "ShiftPlan":
        """Update the shift plan status."""
        self.status = status
        db.add(self)
        db.commit()
        db.refresh(self)
        return self

    def set_output_path(self, db: Session, output_path: str) -> "ShiftPlan":
        """Set the output Excel file path."""
        self.output_path = output_path
        db.add(self)
        db.commit()
        db.refresh(self)
        return self

    def set_plan_data(self, db: Session, week_plans: list[dict]) -> None:
        """Save week plans JSON to the database."""
        self.plan_json = json.dumps(week_plans, ensure_ascii=False)
        db.add(self)
        db.commit()

    def get_plan_data(self) -> list[dict] | None:
        """Load week plans from the stored JSON. Returns None if no plan exists."""
        if not self.plan_json:
            return None
        return json.loads(self.plan_json)

    def delete(self, db: Session) -> None:
        """Delete the shift plan and all related data."""
        db.delete(self)
        db.commit()
