"""EmployeeConstraint model."""

import json

from sqlalchemy import Column, DateTime, ForeignKey, Integer, Text
from sqlalchemy.orm import Session, relationship
from sqlalchemy.sql import func

from app.dal.base import Base


class EmployeeConstraint(Base):
    """EmployeeConstraint model - constraints per employee per shift plan."""

    __tablename__ = "employee_constraints"

    id = Column(Integer, primary_key=True, index=True)
    shift_plan_id = Column(Integer, ForeignKey("shift_plans.id"), nullable=False, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False, index=True)

    # Constraint fields (stored as JSON arrays)
    availability_days = Column(Text, nullable=True)
    unavailable_days = Column(Text, nullable=True)
    max_shifts_per_week = Column(Integer, nullable=True)
    max_hours_per_week = Column(Integer, nullable=True)
    min_rest_hours = Column(Integer, default=11)
    preferred_shift_types = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    shift_plan = relationship("ShiftPlan", back_populates="constraints")
    employee = relationship("Employee", back_populates="constraints")

    @staticmethod
    def create(
        db: Session,
        shift_plan_id: int,
        employee_id: int,
        availability_days: list[str] | None = None,
        unavailable_days: list[str] | None = None,
        max_shifts_per_week: int | None = None,
        max_hours_per_week: int | None = None,
        min_rest_hours: int = 11,
        preferred_shift_types: list[str] | None = None,
        notes: str | None = None,
    ) -> "EmployeeConstraint":
        """Create a new employee constraint."""
        constraint = EmployeeConstraint(
            shift_plan_id=shift_plan_id,
            employee_id=employee_id,
            availability_days=json.dumps(availability_days, ensure_ascii=False)
            if availability_days
            else None,
            unavailable_days=json.dumps(unavailable_days, ensure_ascii=False)
            if unavailable_days
            else None,
            max_shifts_per_week=max_shifts_per_week,
            max_hours_per_week=max_hours_per_week,
            min_rest_hours=min_rest_hours,
            preferred_shift_types=json.dumps(preferred_shift_types, ensure_ascii=False)
            if preferred_shift_types
            else None,
            notes=notes,
        )
        db.add(constraint)
        db.commit()
        db.refresh(constraint)
        return constraint

    @staticmethod
    def get_by_shift_plan(db: Session, shift_plan_id: int) -> list["EmployeeConstraint"]:
        """Get all constraints for a shift plan."""
        return (
            db.query(EmployeeConstraint)
            .filter(EmployeeConstraint.shift_plan_id == shift_plan_id)
            .all()
        )

    @staticmethod
    def get_by_employee_and_plan(
        db: Session, shift_plan_id: int, employee_id: int
    ) -> "EmployeeConstraint | None":
        """Get constraint for a specific employee in a shift plan."""
        return (
            db.query(EmployeeConstraint)
            .filter(
                EmployeeConstraint.shift_plan_id == shift_plan_id,
                EmployeeConstraint.employee_id == employee_id,
            )
            .first()
        )

    def get_availability_days_list(self) -> list[str]:
        """Get availability days as a Python list."""
        if self.availability_days:
            return json.loads(self.availability_days)
        return []

    def get_unavailable_days_list(self) -> list[str]:
        """Get unavailable days as a Python list."""
        if self.unavailable_days:
            return json.loads(self.unavailable_days)
        return []

    def get_preferred_shift_types_list(self) -> list[str]:
        """Get preferred shift types as a Python list."""
        if self.preferred_shift_types:
            return json.loads(self.preferred_shift_types)
        return []

    def update(
        self,
        db: Session,
        availability_days: list[str] | None = None,
        unavailable_days: list[str] | None = None,
        max_shifts_per_week: int | None = None,
        max_hours_per_week: int | None = None,
        min_rest_hours: int | None = None,
        preferred_shift_types: list[str] | None = None,
        notes: str | None = None,
    ) -> "EmployeeConstraint":
        """Update constraint fields."""
        if availability_days is not None:
            self.availability_days = json.dumps(availability_days, ensure_ascii=False)
        if unavailable_days is not None:
            self.unavailable_days = json.dumps(unavailable_days, ensure_ascii=False)
        if max_shifts_per_week is not None:
            self.max_shifts_per_week = max_shifts_per_week
        if max_hours_per_week is not None:
            self.max_hours_per_week = max_hours_per_week
        if min_rest_hours is not None:
            self.min_rest_hours = min_rest_hours
        if preferred_shift_types is not None:
            self.preferred_shift_types = json.dumps(preferred_shift_types, ensure_ascii=False)
        if notes is not None:
            self.notes = notes

        db.add(self)
        db.commit()
        db.refresh(self)
        return self
