"""API core config (§24). Single API prefix keeps routes versionable (/api/v1 later)."""
from __future__ import annotations

from signalcraft.config import settings

API_PREFIX = "/api"

__all__ = ["API_PREFIX", "settings"]
