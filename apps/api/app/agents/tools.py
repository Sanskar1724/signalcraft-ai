"""Named agent tools (§12) with explicit schemas (§35). Deterministic first."""
from __future__ import annotations

from signalcraft import analytics as _analytics
from signalcraft import memory as _memory
from signalcraft import opportunities as _opportunities
from signalcraft import profiles as _profiles
from signalcraft import trends as _trends
from signalcraft.content import critique as _critique
from signalcraft.content import generate_content as _generate
from signalcraft.content import list_content
from signalcraft.research import search as _search

__all__ = ["TOOLS", "TOOL_SCHEMAS"]


def get_user_profile(user_id: int = 1) -> dict:
    """Load the creator profile."""
    p = _profiles.get_profile(user_id)
    return p.__dict__


def get_user_memory(user_id: int = 1, limit: int = 10) -> list[dict]:
    """Load relevant creator memory."""
    return _memory.recall(user_id, limit=limit)


def search_research(user_id: int = 1, query: str = "", limit: int = 10) -> list[dict]:
    """Search stored research documents."""
    return _search(user_id, query, limit)


def get_trending_topics(user_id: int = 1, top_n: int = 10) -> list[dict]:
    """Analyze current trends for this creator."""
    return _trends.detect_trends(user_id, top_n)


def get_content_history(user_id: int = 1, limit: int = 20) -> list[dict]:
    """Load previous content."""
    return list_content(user_id, limit)


def get_content_performance(user_id: int = 1) -> dict:
    """Analyze previous content performance."""
    return _analytics.summary(user_id)


def rank_opportunities(user_id: int = 1, top_n: int = 8) -> list[dict]:
    """Rank personalized content opportunities."""
    return _opportunities.build_opportunities(user_id, top_n)


def generate_content(opportunity_id: int, platform: str = "LinkedIn",
                     user_id: int = 1) -> dict:
    """Generate platform content for an opportunity (brief -> draft -> critique)."""
    res = _generate(opportunity_id, platform=platform, user_id=user_id)
    return {"content": res["content"], "critique": res["critique"]}


def critique_content(body: str, platform: str = "LinkedIn", topic: str = "") -> dict:
    """Critique a draft with the structured rubric."""
    return _critique(body, platform=platform, topic=topic)


TOOLS = {
    "get_user_profile": get_user_profile,
    "get_user_memory": get_user_memory,
    "search_research": search_research,
    "get_trending_topics": get_trending_topics,
    "get_content_history": get_content_history,
    "get_content_performance": get_content_performance,
    "rank_opportunities": rank_opportunities,
    "generate_content": generate_content,
    "critique_content": critique_content,
}

TOOL_SCHEMAS = {name: {"max_calls_per_run": 3, "timeout_s": 30} for name in TOOLS}
TOOL_SCHEMAS["generate_content"]["max_calls_per_run"] = 2
