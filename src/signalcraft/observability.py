"""Structured logs + agent execution traces (§25 observable, no secrets)."""
from __future__ import annotations

import json
import logging
import time
import uuid
from dataclasses import dataclass, field
from typing import Any

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
log = logging.getLogger("signalcraft")

__all__ = ["Trace", "log", "new_request_id"]


def new_request_id() -> str:
    return uuid.uuid4().hex[:12]


@dataclass
class Trace:
    request: str
    steps: list[dict[str, Any]] = field(default_factory=list)
    request_id: str = field(default_factory=new_request_id)
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
        return {"request": self.request, "request_id": self.request_id, "steps": self.steps}

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, default=str)
