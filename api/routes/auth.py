"""Session-based authentication against the WiseCity API."""

from __future__ import annotations

import asyncio
import secrets

from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel
from wisecity import WiseCityClient
from wisecity.exceptions import WiseCityError

router = APIRouter()

# In-memory session store: token → (email, password)
# Wiped on server restart — tokens are not persisted, by design.
_sessions: dict[str, tuple[str, str]] = {}


# ---------------------------------------------------------------------------
# Dependency
# ---------------------------------------------------------------------------

def get_auth(authorization: str | None = Header(default=None)) -> tuple[str, str]:
    """FastAPI dependency — validate Bearer token, return (email, password)."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Autenticación requerida")
    token = authorization.removeprefix("Bearer ").strip()
    creds = _sessions.get(token)
    if not creds:
        raise HTTPException(status_code=401, detail="Sesión inválida o expirada")
    return creds


def get_wisecity_client(
    creds: tuple[str, str] = Depends(get_auth),
) -> WiseCityClient:
    """FastAPI dependency — return an authenticated WiseCityClient."""
    email, password = creds
    return WiseCityClient(email=email, password=password)


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
    Validate WiseCity credentials by making a live API call.
    On success, issue a random session token (256-bit entropy).
    The password is stored only in server memory — never returned to the client.
    """
    try:
        client = WiseCityClient(email=body.email, password=body.password)
        await asyncio.to_thread(client.devices.list)
    except WiseCityError:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    except Exception:
        raise HTTPException(status_code=502, detail="Error conectando con WiseCity")

    from api import database
    token = secrets.token_urlsafe(32)   # 256 bits of randomness
    _sessions[token] = (body.email, body.password)
    return LoginResponse(token=token, has_passkey=database.user_has_passkey(body.email))


@router.post("/auth/logout")
async def logout(authorization: str | None = Header(default=None)) -> dict:
    """Invalidate the current session token."""
    if authorization and authorization.startswith("Bearer "):
        token = authorization.removeprefix("Bearer ").strip()
        _sessions.pop(token, None)
    return {"ok": True}


@router.get("/auth/check")
async def check_auth(_creds: tuple[str, str] = Depends(get_auth)) -> dict:
    """Verify that the current session token is still valid."""
    return {"ok": True}
