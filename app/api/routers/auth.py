"""Auth API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr

from app.auth import (
    create_access_token,
    get_current_manager,
    hash_password,
    verify_password,
)
from app.dal import get_session
from app.dal.models import Manager, ManagerRole

router = APIRouter(prefix="/auth", tags=["auth"])


class SignupRequest(BaseModel):
    """Signup request body."""

    email: EmailStr
    password: str
    name: str
    role: ManagerRole


class SigninRequest(BaseModel):
    """Signin request body."""

    email: EmailStr
    password: str


class ManagerInfo(BaseModel):
    """Manager information returned in responses."""

    id: int
    email: str
    name: str
    role: ManagerRole

    model_config = {"from_attributes": True}


class AuthResponse(BaseModel):
    """Authentication response with token and manager info."""

    access_token: str
    token_type: str = "bearer"
    manager: ManagerInfo


@router.post("/signup", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def signup(request: SignupRequest) -> AuthResponse:
    """Register a new manager account."""
    db = get_session()
    try:
        existing = Manager.get_by_email(db, request.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered",
            )

        hashed = hash_password(request.password)
        manager = Manager.create(
            db,
            email=request.email,
            hashed_password=hashed,
            name=request.name,
            role=request.role,
        )

        token = create_access_token(manager.id)
        return AuthResponse(
            access_token=token,
            manager=ManagerInfo.model_validate(manager),
        )
    finally:
        db.close()


@router.post("/signin", response_model=AuthResponse)
def signin(request: SigninRequest) -> AuthResponse:
    """Sign in with email and password."""
    db = get_session()
    try:
        manager = Manager.get_by_email(db, request.email)
        if not manager:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        if not verify_password(request.password, manager.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        token = create_access_token(manager.id)
        return AuthResponse(
            access_token=token,
            manager=ManagerInfo.model_validate(manager),
        )
    finally:
        db.close()


@router.get("/me", response_model=ManagerInfo)
def get_me(manager: Manager = Depends(get_current_manager)) -> ManagerInfo:
    """Get the current authenticated manager's information."""
    return ManagerInfo.model_validate(manager)
