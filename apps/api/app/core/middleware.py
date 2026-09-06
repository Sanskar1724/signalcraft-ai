"""Request-ID middleware (§25): every request gets an ID, propagated in logs/headers."""
from __future__ import annotations

from contextvars import ContextVar

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from signalcraft.observability import log, new_request_id

request_id_ctx: ContextVar[str] = ContextVar("request_id", default="-")


class RequestIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        rid = request.headers.get("X-Request-ID") or new_request_id()
        request_id_ctx.set(rid)
        log.info("request %s %s rid=%s", request.method, request.url.path, rid)
        response = await call_next(request)
        response.headers["X-Request-ID"] = rid
        return response
