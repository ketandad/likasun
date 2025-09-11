"""Authentication endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel

from ..core.security import authenticate_user, create_access_token, users_db
from ..services.audit import record
from ..core.license import check_seats


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()) -> Token:
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect username or password",
        )
    access_token = create_access_token(
        data={"sub": user["username"], "role": user["role"]}
    )
    record("LOGIN", actor=user.get("username"))
    return Token(access_token=access_token)


class UserIn(BaseModel):
    username: str
    password: str
    role: str = "viewer"


@router.post("/register")
async def register(user: UserIn) -> dict:
    check_seats(len(users_db) + 1)
    if user.username in users_db:
        raise HTTPException(status_code=400, detail="User exists")
    users_db[user.username] = {
        "username": user.username,
        "password": user.password,
        "role": user.role,
    }
    return {"status": "ok"}

