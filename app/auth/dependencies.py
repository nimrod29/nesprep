"""FastAPI authentication dependencies."""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.auth.jwt import TokenError, decode_access_token
from app.dal import get_session
from app.dal.models import Manager

security = HTTPBearer()


def get_current_manager(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> Manager:
    """FastAPI dependency to get the current authenticated manager.

    Extracts the JWT token from the Authorization header,
    validates it, and returns the Manager object.

    Raises HTTPException 401 if authentication fails.
    """
    token = credentials.credentials

    try:
        manager_id = decode_access_token(token)
    except TokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        ) from e

    db = get_session()
    try:
        manager = Manager.get_by_id(db, manager_id)
        if manager is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Manager not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return manager
    finally:
        db.close()
