"""Security utilities for authentication and authorization."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Dict, Optional


import jwt
import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from .config import settings


# Simple in-memory user store
users_db: Dict[str, Dict[str, Any]] = {}


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")


def authenticate_user(username: str, password: str) -> Optional[dict]:
    user = users_db.get(username)
    if not user:
        return None
    hashed = user.get("password")
    if not hashed or not bcrypt.checkpw(password.encode(), hashed.encode()):
        return None
    return user


async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
    except jwt.PyJWTError:
        raise credentials_exception from None
    username: str | None = payload.get("sub")
    if username is None or username not in users_db:
        raise credentials_exception
    return users_db[username]


class RoleChecker:
    """Dependency that checks a user's role."""

    def __init__(self, roles: list[str]):
        self.roles = roles

    def __call__(self, user: dict = Depends(get_current_user)) -> None:
        role = user.get("role")
        if role not in self.roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Operation not permitted",
            )


__all__ = [
    "authenticate_user",
    "create_access_token",
    "get_current_user",
    "oauth2_scheme",
    "RoleChecker",
    "users_db",
]

