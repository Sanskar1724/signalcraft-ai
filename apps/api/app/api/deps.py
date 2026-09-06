"""API dependencies (§24 auth, §25 request tracking). Single-user MVP (§29)."""
from __future__ import annotations

from fastapi import Header, HTTPException

from signalcraft.config import settings

from ..core.middleware import request_id_ctx


async def require_key(x_api_key: str | None = Header(default=None)) -> None:
    """API-key auth. Open local mode when SIGNALCRAFT_API_KEY is unset (documented)."""
    if settings.api_key and x_api_key != settings.api_key:
        raise HTTPException(status_code=401, detail="invalid API key")


async def get_user_id() -> int:
    return 1


def current_request_id() -> str:
    return request_id_ctx.get()
