"""Error envelope (§23 proper errors, §32 never silently fail)."""
from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from .middleware import request_id_ctx


def _envelope(status: int, code: str, message: str, request: Request):
    return JSONResponse(
        status_code=status,
        content={"error": {"code": code, "message": message,
                           "request_id": request_id_ctx.get()}},
        headers={"X-Request-ID": request_id_ctx.get()},
    )


def register_handlers(app: FastAPI) -> None:
    @app.exception_handler(ValueError)
    async def _value(request: Request, exc: ValueError):
        return _envelope(400, "bad_request", str(exc), request)

    @app.exception_handler(RuntimeError)
    async def _runtime(request: Request, exc: RuntimeError):
        return _envelope(429, "rate_limited", str(exc), request)

    @app.exception_handler(TimeoutError)
    async def _timeout(request: Request, exc: TimeoutError):
        return _envelope(504, "timeout", str(exc), request)

    @app.exception_handler(Exception)
    async def _other(request: Request, exc: Exception):
        return _envelope(500, "internal_error", f"{type(exc).__name__}: {exc}", request)
