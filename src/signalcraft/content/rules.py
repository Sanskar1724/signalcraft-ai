"""Platform rules as configuration (§14), not scattered hard-coded strings.

Each platform declares its structure, limits, and defaults. Formatters in
platforms.py render from these rules; add a new platform by adding one entry.
"""
from __future__ import annotations

PLATFORM_RULES: dict[str, dict] = {
    "LinkedIn": {
        "structure": ["hook", "context", "insight", "explanation", "takeaway", "cta"],
        "min_words": 30,
        "max_words": 600,
        "default_cta": "What is working for you?",
        "takeaways": ["Why it matters now", "One concrete example", "What to try this week"],
    },
    "X": {
        "structure": ["strong opening", "concise insight", "supporting points", "thread"],
        "min_words": 15,
        "max_words": 600,
        "thread": True,
        "default_cta": "",
    },
    "Blog": {
        "structure": ["title", "introduction", "sections", "evidence", "examples", "conclusion"],
        "min_words": 60,
        "max_words": 3000,
        "default_cta": "Subscribe for the next deep dive.",
        "sections": ["Why now", "How it works", "What to do next"],
    },
}

__all__ = ["PLATFORM_RULES", "get_rules"]


def get_rules(platform: str) -> dict:
    return PLATFORM_RULES.get(platform, PLATFORM_RULES["LinkedIn"])
