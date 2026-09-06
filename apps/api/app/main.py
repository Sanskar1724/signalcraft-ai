"""SignalCraft API (§4-§5, §23). Thin FastAPI layer over the domain modules."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from fastapi import FastAPI  # noqa: E402
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402

from signalcraft.config import settings  # noqa: E402

from .api.router import router  # noqa: E402
from .core.errors import register_handlers  # noqa: E402
from .core.middleware import RequestIdMiddleware  # noqa: E402

app = FastAPI(title="SignalCraft AI", version="0.1.0")
app.add_middleware(RequestIdMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.cors_origins.split(",") if o.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
register_handlers(app)
app.include_router(router)

__all__ = ["app"]
