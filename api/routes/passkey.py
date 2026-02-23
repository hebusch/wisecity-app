"""WebAuthn / Passkey routes — biometric login and registration."""

from __future__ import annotations

import json
import os
import secrets

from urllib.parse import urlparse

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel

from webauthn import (
    generate_authentication_options,
    generate_registration_options,
    options_to_json,
    verify_authentication_response,
    verify_registration_response,
)
from webauthn.helpers import base64url_to_bytes, bytes_to_base64url
from webauthn.helpers.structs import (
    AuthenticatorAssertionResponse,
    AuthenticatorAttestationResponse,
    AuthenticatorSelectionCriteria,
    AuthenticationCredential,
    RegistrationCredential,
    ResidentKeyRequirement,
    UserVerificationRequirement,
)

import bcrypt

from api import database
from api.routes.auth import _sessions, get_auth

router = APIRouter()

RP_NAME = "WiseCity GPS Dashboard"
_DEFAULT_RP_ID     = os.environ.get("WEBAUTHN_RP_ID", "localhost")
_DEFAULT_RP_ORIGIN = os.environ.get("WEBAUTHN_ORIGIN", "http://localhost:8000")

# Short-lived in-memory challenge stores (wiped on restart, by design)
_reg_challenges: dict[str, bytes] = {}   # user_id  → challenge bytes
_auth_challenges: dict[str, bytes] = {}  # challenge_id → challenge bytes


def _rp_config(request: Request) -> tuple[str, str]:
    """Derive RP_ID and origin from the incoming request.

    This lets the same backend work from localhost, ngrok, or any domain
    without changing env vars.
    """
    origin = request.headers.get("origin") or _DEFAULT_RP_ORIGIN
    parsed = urlparse(origin)
    rp_id = parsed.hostname or _DEFAULT_RP_ID
    return rp_id, origin


# ── Request / response models ─────────────────────────────────────────────────

class RegBeginRequest(BaseModel):
    email: str

class RegAttestationResponse(BaseModel):
    clientDataJSON: str
    attestationObject: str
    transports: list[str] = []

class RegCompleteRequest(BaseModel):
    id: str
    rawId: str
    response: RegAttestationResponse
    type: str

class AuthCompleteRequest(BaseModel):
    challenge_id: str
    credential: dict


class DeletePasskeyRequest(BaseModel):
    password: str


# ── Registration ──────────────────────────────────────────────────────────────

@router.post("/auth/passkey/register/begin")
async def passkey_register_begin(
    body: RegBeginRequest,
    request: Request,
    email: str = Depends(get_auth),
) -> dict:
    """Start WebAuthn registration (requires active session)."""
    rp_id, _ = _rp_config(request)
    options = generate_registration_options(
        rp_id=rp_id,
        rp_name=RP_NAME,
        user_id=email.encode(),
        user_name=email,
        user_display_name=email,
        authenticator_selection=AuthenticatorSelectionCriteria(
            resident_key=ResidentKeyRequirement.REQUIRED,
            user_verification=UserVerificationRequirement.REQUIRED,
        ),
    )
    _reg_challenges[email] = options.challenge
    return json.loads(options_to_json(options))


@router.post("/auth/passkey/register/complete")
async def passkey_register_complete(
    body: RegCompleteRequest,
    request: Request,
    email: str = Depends(get_auth),
) -> dict:
    """Complete registration and persist WebAuthn credential."""
    rp_id, origin = _rp_config(request)
    challenge = _reg_challenges.pop(email, None)
    if challenge is None:
        raise HTTPException(400, "No hay registro pendiente para este usuario")

    credential = RegistrationCredential(
        id=body.id,
        raw_id=base64url_to_bytes(body.rawId),
        response=AuthenticatorAttestationResponse(
            client_data_json=base64url_to_bytes(body.response.clientDataJSON),
            attestation_object=base64url_to_bytes(body.response.attestationObject),
        ),
        type="public-key",
    )
    try:
        verification = verify_registration_response(
            credential=credential,
            expected_challenge=challenge,
            expected_rp_id=rp_id,
            expected_origin=origin,
            require_user_verification=True,
        )
    except Exception as exc:
        raise HTTPException(400, f"Registro inválido: {exc}") from exc

    # Persist the WebAuthn credential
    database.save_passkey_credential(
        credential_id=bytes_to_base64url(verification.credential_id),
        user_id=email,
        public_key=bytes_to_base64url(verification.credential_public_key),
        sign_count=verification.sign_count,
        transports=json.dumps(body.response.transports),
    )
    return {"ok": True}


# ── Authentication ────────────────────────────────────────────────────────────

@router.post("/auth/passkey/login/begin")
async def passkey_login_begin(request: Request) -> dict:
    """Generate a WebAuthn authentication challenge (unauthenticated)."""
    rp_id, _ = _rp_config(request)
    options = generate_authentication_options(
        rp_id=rp_id,
        user_verification=UserVerificationRequirement.REQUIRED,
    )
    challenge_id = secrets.token_urlsafe(16)
    _auth_challenges[challenge_id] = options.challenge
    result = json.loads(options_to_json(options))
    result["challenge_id"] = challenge_id
    return result


@router.post("/auth/passkey/login/complete")
async def passkey_login_complete(body: AuthCompleteRequest, request: Request) -> dict:
    """Verify WebAuthn assertion and issue a session token."""
    _, origin = _rp_config(request)
    rp_id = urlparse(origin).hostname or _DEFAULT_RP_ID
    challenge = _auth_challenges.pop(body.challenge_id, None)
    if challenge is None:
        raise HTTPException(400, "Challenge inválido o expirado")

    raw = body.credential
    try:
        credential = AuthenticationCredential(
            id=raw["id"],
            raw_id=base64url_to_bytes(raw["rawId"]),
            response=AuthenticatorAssertionResponse(
                client_data_json=base64url_to_bytes(raw["response"]["clientDataJSON"]),
                authenticator_data=base64url_to_bytes(raw["response"]["authenticatorData"]),
                signature=base64url_to_bytes(raw["response"]["signature"]),
                user_handle=(
                    base64url_to_bytes(raw["response"]["userHandle"])
                    if raw["response"].get("userHandle") else None
                ),
            ),
            type="public-key",
        )
    except Exception as exc:
        raise HTTPException(400, f"Credencial inválida: {exc}") from exc

    stored = database.get_passkey_credential(raw["id"])
    if not stored:
        raise HTTPException(401, "Credencial no registrada en este servidor")

    try:
        verification = verify_authentication_response(
            credential=credential,
            expected_challenge=challenge,
            expected_rp_id=rp_id,
            expected_origin=origin,
            credential_public_key=base64url_to_bytes(stored["public_key"]),
            credential_current_sign_count=stored["sign_count"],
            require_user_verification=True,
        )
    except Exception as exc:
        raise HTTPException(401, f"Autenticación inválida: {exc}") from exc

    database.update_passkey_sign_count(raw["id"], verification.new_sign_count)

    token = secrets.token_urlsafe(32)
    _sessions[token] = stored["user_id"]  # user_id == email
    return {"token": token}


# ── Delete passkey ────────────────────────────────────────────────────────────

@router.delete("/auth/passkey")
async def delete_passkey(
    body: DeletePasskeyRequest,
    email: str = Depends(get_auth),
) -> dict:
    """Delete passkey for the authenticated user after password verification."""
    user = database.get_local_user_by_email(email)
    if not user or not bcrypt.checkpw(body.password.encode(), user["password_hash"].encode()):
        raise HTTPException(401, "Contraseña incorrecta")
    database.delete_passkey_for_user(email)
    return {"ok": True}


# ── Public email check (no auth required) ────────────────────────────────────

@router.get("/auth/passkey/check")
async def passkey_check(email: str) -> dict:
    """Return whether a given email has a registered passkey. No auth required."""
    return {"has_passkey": database.user_has_passkey(email)}
