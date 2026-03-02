"""JWT token utilities."""

from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt

from app.config import settings


class TokenError(Exception):
    """Raised when token validation fails."""

    pass


def create_access_token(manager_id: int) -> str:
    """Create a JWT access token for a manager."""
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload = {
        "sub": str(manager_id),
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> int:
    """Decode and validate a JWT access token.

    Returns the manager_id from the token.
    Raises TokenError if the token is invalid or expired.
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        manager_id_str = payload.get("sub")
        if manager_id_str is None:
            raise TokenError("Token missing subject claim")
        return int(manager_id_str)
    except JWTError as e:
        raise TokenError(f"Invalid token: {e}") from e
    except ValueError as e:
        raise TokenError(f"Invalid manager ID in token: {e}") from e
