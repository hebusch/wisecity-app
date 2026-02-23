"""Session-based authentication against the local user database."""

from __future__ import annotations

import os
import secrets

import bcrypt
from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel
from wisecity import WiseCityClient

router = APIRouter()

# In-memory session store: token → email
# Wiped on server restart — tokens are not persisted, by design.
_sessions: dict[str, str] = {}


# ---------------------------------------------------------------------------
# Dependencies
# ---------------------------------------------------------------------------

def get_auth(authorization: str | None = Header(default=None)) -> str:
    """FastAPI dependency — validate Bearer token, return email."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Autenticación requerida")
    token = authorization.removeprefix("Bearer ").strip()
    email = _sessions.get(token)
    if not email:
        raise HTTPException(status_code=401, detail="Sesión inválida o expirada")
    return email


def get_wisecity_client(_: str = Depends(get_auth)) -> WiseCityClient:
    """FastAPI dependency — return a WiseCityClient using env credentials."""
    return WiseCityClient(
        email=os.environ["WISECITY_EMAIL"],
        password=os.environ["WISECITY_PASSWORD"],
    )


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

class LoginRequest(BaseModel):
    email: str
    password: str


class LoginResponse(BaseModel):
    token: str
    has_passkey: bool


@router.post("/auth/login", response_model=LoginResponse)
async def login(body: LoginRequest) -> LoginResponse:
    """
    Validate credentials against the local user database.
    On success, issue a random session token (256-bit entropy).
    """
    from api import database

    user = database.get_local_user_by_email(body.email)
    if not user or not bcrypt.checkpw(body.password.encode(), user["password_hash"].encode()):
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    token = secrets.token_urlsafe(32)
    _sessions[token] = body.email
    return LoginResponse(token=token, has_passkey=database.user_has_passkey(body.email))


@router.post("/auth/logout")
async def logout(authorization: str | None = Header(default=None)) -> dict:
    """Invalidate the current session token."""
    if authorization and authorization.startswith("Bearer "):
        token = authorization.removeprefix("Bearer ").strip()
        _sessions.pop(token, None)
    return {"ok": True}


@router.get("/auth/check")
async def check_auth(_email: str = Depends(get_auth)) -> dict:
    """Verify that the current session token is still valid."""
    return {"ok": True}


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str


@router.post("/auth/change-password")
async def change_password(
    body: ChangePasswordRequest,
    email: str = Depends(get_auth),
) -> dict:
    """Change the password for the authenticated user."""
    from api import database

    user = database.get_local_user_by_email(email)
    if not user or not bcrypt.checkpw(body.current_password.encode(), user["password_hash"].encode()):
        raise HTTPException(status_code=401, detail="Contraseña actual incorrecta")

    new_hash = bcrypt.hashpw(body.new_password.encode(), bcrypt.gensalt()).decode()
    database.update_local_user_password(email, new_hash)
    return {"ok": True}
