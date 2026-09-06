"""Personalization service (§13): build ONE Creator Context from everything.

User + Profile + Audience + Goals + Preferences + Topics + Content History
+ Performance + Memory  →  Creator Context dict consumed by the agent,
the brief builder and the opportunity engine. Pages never reconstruct this.
"""
from __future__ import annotations

from . import analytics as _analytics
from . import memory as _memory
from . import preferences as _prefs
from .profiles import get_profile
from .taxonomy import list_audiences, list_topics

__all__ = ["build_context"]


def build_context(user_id: int = 1) -> dict:
    from .auth import get_user
    user = get_user(user_id)
    profile = get_profile(user_id)
    prefs = _prefs.get_preferences(user_id)
    summary = _analytics.summary(user_id)
    mem = _memory.recall(user_id, limit=10)
    return {
        "user": {"id": user["id"], "name": user["name"]},
        "niche": profile.niche,
        "expertise": profile.expertise,
        "expertise_level": profile.expertise_level,
        "audience": profile.audience,
        "audience_segments": [a["name"] for a in list_audiences(user_id)],
        "goals": [g.strip() for g in (profile.goals or "").split(",") if g.strip()],
        "platforms": profile.platforms,
        "tone": prefs.get("tone") or profile.tone,
        "writing_style": profile.writing_style,
        "topics": profile.topics,
        "avoid_topics": profile.avoid_topics,
        "formats": prefs.get("formats") or [],
        "frequency": prefs.get("frequency") or "",
        "research_depth": prefs.get("research_depth") or "standard",
        "use_trends": bool(prefs.get("use_trends", 1)),
        "cta_pref": prefs.get("cta_pref") or "question",
        "tracked_topics": [t["name"] for t in list_topics(user_id)],
        "posts": summary["posts"],
        "avg_engagement": summary["avg_engagement"],
        "best_topics": [t["topic"] for t in summary.get("best_topics", [])],
        "weak_topics": [t["topic"] for t in summary.get("weak_topics", [])],
        "best_platforms": [p.get("platform") for p in summary.get("by_platform", [])[:2]],
        "memories": [f"{m['kind']}:{m['key']}" for m in mem],
    }
