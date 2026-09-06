"""API dependencies (§31 auth, §25 request tracking). Bearer sessions with
single-user dev fallback: tokenless requests resolve to user 1 only while
user 1 has no password (fresh/seeded installs)."""
from __future__ import annotations

from fastapi import Depends, Header, HTTPException

from signalcraft import auth as _auth
from signalcraft.config import settings

from ..core.middleware import request_id_ctx


async def require_key(x_api_key: str | None = Header(default=None)) -> None:
    """API-key auth. Open local mode when SIGNALCRAFT_API_KEY is unset (documented)."""
    if settings.api_key and x_api_key != settings.api_key:
        raise HTTPException(status_code=401, detail="invalid API key")


async def get_current_user(authorization: str | None = Header(default=None)) -> dict:
    if authorization and authorization.lower().startswith("bearer "):
        user = _auth.get_user_by_token(authorization[7:].strip())
        if user is None:
            raise HTTPException(status_code=401, detail="invalid session")
        return user
    legacy = _auth.get_user(1)
    if legacy and not _has_password(1):
        return legacy
    raise HTTPException(status_code=401, detail="login required")


async def get_user_id(user: dict = Depends(get_current_user)) -> int:
    return int(user["id"])


def _has_password(user_id: int) -> bool:
    from signalcraft.db import get_conn
    conn = get_conn()
    try:
        row = conn.execute("SELECT password_hash FROM users WHERE id=?", (user_id,)).fetchone()
        return bool(row and row["password_hash"])
    finally:
        conn.close()


def current_request_id() -> str:
    return request_id_ctx.get()
