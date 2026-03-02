"""Auth API endpoints.

Simple auth for development - creates manager on first login.
"""

from fastapi import APIRouter
from pydantic import BaseModel

from app.dal import get_session
from app.dal.models import Manager

router = APIRouter(prefix="/auth", tags=["auth"])


class LoginRequest(BaseModel):
    """Login request body."""

    manager_id: int | None = None
    name: str | None = None


class LoginResponse(BaseModel):
    """Login response body."""

    manager_id: int
    name: str | None


@router.post("/login", response_model=LoginResponse)
def login(request: LoginRequest) -> LoginResponse:
    """Login or create a manager.

    For development: if manager_id is provided, returns that manager.
    If not, creates a new manager with the given name.
    """
    db = get_session()
    try:
        if request.manager_id:
            manager = Manager.get_by_id(db, request.manager_id)
            if manager:
                return LoginResponse(manager_id=manager.id, name=manager.name)

        name = request.name or "Manager"
        email = f"{name.lower().replace(' ', '_')}_{id(request)}@nesprep.local"
        manager = Manager.create(db, email=email, hashed_password="dev", name=name)

        return LoginResponse(manager_id=manager.id, name=manager.name)
    finally:
        db.close()
