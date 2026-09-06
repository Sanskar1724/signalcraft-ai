"""Input validation + lightweight rate limiting (§23). Local MVP scope."""
from __future__ import annotations

import time
from collections import defaultdict

__all__ = ["MAX_REQUEST_LEN", "MAX_TOOL_CALLS", "validate_request",
           "check_rate_limit", "Budget"]

MAX_REQUEST_LEN = 2000
MAX_TOOL_CALLS = 8
_AGENT_BUDGET = 60.0  # seconds per agent run (§11 execution-time limit)
_hits: defaultdict[str, list[float]] = defaultdict(list)


def validate_request(text: str) -> str:
    text = (text or "").strip()
    if not text:
        raise ValueError("request must be non-empty")
    if len(text) > MAX_REQUEST_LEN:
        raise ValueError(f"request too long (max {MAX_REQUEST_LEN} chars)")
    return text


def check_rate_limit(key: str = "agent", limit: int = 20, window_s: int = 60) -> None:
    now = time.time()
    recent = [t for t in _hits[key] if now - t < window_s]
    if len(recent) >= limit:
        raise RuntimeError("rate limit exceeded, try again shortly")
    recent.append(now)
    _hits[key] = recent


class Budget:
    """Simple execution-time guard for agent runs."""

    def __init__(self, seconds: float = _AGENT_BUDGET):
        self.deadline = time.time() + seconds

    def check(self) -> None:
        if time.time() > self.deadline:
            raise TimeoutError("agent execution budget exceeded")
