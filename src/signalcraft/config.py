"""Central configuration (§24 env secrets, §10 configurable weights, §34 model routing)."""
from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass, field
from pathlib import Path

try:
    from dotenv import load_dotenv  # type: ignore
    load_dotenv()
except Exception as e:
    logging.getLogger("signalcraft").debug("dotenv not loaded: %s", e)

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DB = ROOT / "data" / "signalcraft.db"

# §10 example weights: 30% growth, 25% freshness, 20% relevance,
# 15% source momentum, 10% novelty. Overridable via TREND_WEIGHTS_JSON.
DEFAULT_TREND_WEIGHTS = {
    "growth": 0.30, "freshness": 0.25, "relevance": 0.20,
    "source_momentum": 0.15, "novelty": 0.10,
}

# §11 opportunity weights (must sum to 1.0).
DEFAULT_OPP_WEIGHTS = {
    "trend": 0.45, "user_relevance": 0.20, "audience_fit": 0.15,
    "freshness": 0.10, "low_competition": 0.10,
}


def _json_env(name: str, default: dict) -> dict:
    try:
        raw = os.getenv(name, "")
        return {**default, **json.loads(raw)} if raw else dict(default)
    except Exception:
        return dict(default)


@dataclass
class Settings:
    db_path: Path = field(default_factory=lambda: Path(os.getenv("SIGNALCRAFT_DB_PATH", str(DEFAULT_DB))))
    env: str = os.getenv("SIGNALCRAFT_ENV", "dev")
    api_key: str = os.getenv("SIGNALCRAFT_API_KEY", "")
    cors_origins: str = os.getenv("CORS_ORIGINS", "http://localhost:3000")
    google_client_id: str = os.getenv("GOOGLE_CLIENT_ID", "")
    google_client_secret: str = os.getenv("GOOGLE_CLIENT_SECRET", "")
    frontend_url: str = os.getenv("FRONTEND_URL", "http://localhost:3001")
    backend_url: str = os.getenv("BACKEND_URL", "http://localhost:8001")
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_base_url: str = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    openrouter_api_key: str = os.getenv("OPENROUTER_API_KEY", "")
    openrouter_base_url: str = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
    cheap_model: str = os.getenv("CHEAP_MODEL", "mock")
    strong_model: str = os.getenv("STRONG_MODEL", "mock")
    primary_model: str = os.getenv("PRIMARY_MODEL", "mock")
    quality_threshold: float = float(os.getenv("QUALITY_THRESHOLD", "7.5"))
    max_retries: int = int(os.getenv("MAX_RETRIES", "1"))
    trend_weights: dict = field(default_factory=lambda: _json_env("TREND_WEIGHTS_JSON", DEFAULT_TREND_WEIGHTS))
    opp_weights: dict = field(default_factory=lambda: _json_env("OPP_WEIGHTS_JSON", DEFAULT_OPP_WEIGHTS))

    def ensure_dirs(self) -> None:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)


settings = Settings()

__all__ = ["DEFAULT_OPP_WEIGHTS", "DEFAULT_TREND_WEIGHTS", "Settings", "settings"]
