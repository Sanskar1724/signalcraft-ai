"""Platform rules as configuration (§14), not scattered hard-coded strings.

Each platform declares its structure, limits, and defaults. Formatters in
platforms.py render from these rules; add a new platform by adding one entry.
"""
from __future__ import annotations

PLATFORM_RULES: dict[str, dict] = {
    "LinkedIn": {
        "structure": ["hook", "context", "insight", "explanation", "takeaway", "cta"],
        "max_words": 500,
        "default_cta": "What is working for you?",
        "takeaways": ["Why it matters now", "One concrete example", "What to try this week"],
    },
    "X": {
        "structure": ["strong opening", "concise insight", "supporting points", "thread"],
        "max_words": 280,
        "thread": True,
        "default_cta": "",
    },
    "Blog": {
        "structure": ["title", "introduction", "sections", "evidence", "examples", "conclusion"],
        "min_words": 200,
        "default_cta": "Subscribe for the next deep dive.",
        "sections": ["Why now", "How it works", "What to do next"],
    },
}

__all__ = ["PLATFORM_RULES", "get_rules"]


def get_rules(platform: str) -> dict:
    return PLATFORM_RULES.get(platform, PLATFORM_RULES["LinkedIn"])
