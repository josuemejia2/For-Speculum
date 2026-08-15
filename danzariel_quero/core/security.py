from __future__ import annotations

from fastapi import Header, HTTPException

from danzariel_quero.core.config import settings


def require_token(
    authorization: str | None = Header(default=None),
    x_dq_token: str | None = Header(default=None),
) -> None:
    expected = settings.secret_token
    supplied = x_dq_token

    if authorization and authorization.lower().startswith("bearer "):
        supplied = authorization[7:].strip()

    if not supplied or supplied != expected:
        raise HTTPException(status_code=401, detail="Token invalido o ausente")
