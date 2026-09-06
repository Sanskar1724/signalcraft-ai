"""Central configuration. Env-first, sane offline defaults."""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

try:
    from dotenv import load_dotenv  # type: ignore
    load_dotenv()
except Exception:
    pass

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DB = ROOT / "data" / "signalcraft.db"


@dataclass
class Settings:
    db_path: Path = field(default_factory=lambda: Path(os.getenv("SIGNALCRAFT_DB_PATH", str(DEFAULT_DB))))
    env: str = os.getenv("SIGNALCRAFT_ENV", "dev")
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_base_url: str = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    primary_model: str = os.getenv("PRIMARY_MODEL", "mock")

    def ensure_dirs(self) -> None:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)


settings = Settings()
