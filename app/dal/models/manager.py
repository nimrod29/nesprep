"""Manager model."""

from enum import Enum

from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Session, relationship
from sqlalchemy.sql import func

from app.dal.base import Base


class ManagerRole(str, Enum):
    """Manager role types."""

    BOUTIQUE = "מנהל בוטיק"
    REGIONAL = "מנהל אזור"
    SENIOR = "הנהלה בכירה"


class Manager(Base):
    """Manager account model - users who create shift plans."""

    __tablename__ = "managers"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    role = Column(SQLEnum(ManagerRole), nullable=False, default=ManagerRole.BOUTIQUE)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    employees = relationship("Employee", back_populates="manager", cascade="all, delete-orphan")
    shift_plans = relationship("ShiftPlan", back_populates="manager", cascade="all, delete-orphan")

    @staticmethod
    def create(
        db: Session,
        email: str,
        hashed_password: str,
        name: str,
        role: ManagerRole = ManagerRole.BOUTIQUE,
    ) -> "Manager":
        """Create a new manager."""
        manager = Manager(
            email=email,
            hashed_password=hashed_password,
            name=name,
            role=role,
        )
        db.add(manager)
        db.commit()
        db.refresh(manager)
        return manager

    @staticmethod
    def get_by_id(db: Session, manager_id: int) -> "Manager | None":
        """Get manager by ID."""
        return db.query(Manager).filter(Manager.id == manager_id).first()

    @staticmethod
    def get_by_email(db: Session, email: str) -> "Manager | None":
        """Get manager by email."""
        return db.query(Manager).filter(Manager.email == email).first()
