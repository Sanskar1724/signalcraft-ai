"""Background-ready refresh pipeline (§21). Synchronous in MVP; move to a
worker/cron later without changing callers: jobs.run_refresh() is the job."""
from __future__ import annotations

from .opportunities import build_opportunities
from .research import collect_and_store
from .trends import detect_trends

__all__ = ["run_refresh"]


def run_refresh(user_id: int = 1, limit: int = 20, use_live: bool = True) -> dict:
    research = collect_and_store(limit=limit, user_id=user_id, use_live=use_live)
    trends = detect_trends(user_id=user_id)
    opps = build_opportunities(user_id=user_id)
    return {"research": len(research), "trends": len(trends), "opportunities": len(opps)}
