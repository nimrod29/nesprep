"""Employee model."""

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Session, relationship
from sqlalchemy.sql import func

from app.dal.base import Base


class Employee(Base):
    """Employee model - workers managed by a Manager."""

    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    manager_id = Column(Integer, ForeignKey("managers.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    phone = Column(String(50), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    manager = relationship("Manager", back_populates="employees")
    constraints = relationship("EmployeeConstraint", back_populates="employee")

    @staticmethod
    def create(
        db: Session,
        manager_id: int,
        name: str,
        phone: str | None = None,
        notes: str | None = None,
    ) -> "Employee":
        """Create a new employee."""
        employee = Employee(
            manager_id=manager_id,
            name=name,
            phone=phone,
            notes=notes,
        )
        db.add(employee)
        db.commit()
        db.refresh(employee)
        return employee

    @staticmethod
    def get_by_id(db: Session, employee_id: int) -> "Employee | None":
        """Get employee by ID."""
        return db.query(Employee).filter(Employee.id == employee_id).first()

    @staticmethod
    def get_by_manager(db: Session, manager_id: int) -> list["Employee"]:
        """Get all employees for a manager."""
        return db.query(Employee).filter(Employee.manager_id == manager_id).all()

    @staticmethod
    def get_by_name_and_manager(db: Session, manager_id: int, name: str) -> "Employee | None":
        """Get employee by name within a manager's employees."""
        return (
            db.query(Employee)
            .filter(Employee.manager_id == manager_id, Employee.name == name)
            .first()
        )
