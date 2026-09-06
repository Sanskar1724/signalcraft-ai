"""Structured logs + agent execution traces (observable, no secrets)."""
from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass, field
from typing import Any

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
log = logging.getLogger("signalcraft")


@dataclass
class Trace:
    request: str
    steps: list[dict[str, Any]] = field(default_factory=list)
    _t0: float = field(default_factory=time.time, repr=False)

    def add(self, stage: str, detail: Any = None, **extra: Any) -> None:
        self.steps.append({
            "t": round(time.time() - self._t0, 3),
            "stage": stage,
            "detail": detail,
            **extra,
        })
        log.info("trace stage=%s detail=%s", stage, str(detail)[:300])

    def to_dict(self) -> dict[str, Any]:
        return {"request": self.request, "steps": self.steps}

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, default=str)
