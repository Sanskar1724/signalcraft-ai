"""Versioned, reusable prompt templates (§22). No giant inline prompts.

Each template has a name + version. Structured output is validated with
Pydantic schemas (see schemas.py) — never blindly trusted.
"""
from __future__ import annotations

TEMPLATES: dict[str, dict] = {
    "research_summary": {
        "version": 1,
        "template": ("Summarize this research for a creator in niche '{niche}'.\n"
                     "Title: {title}\nSummary: {summary}\n\n"
                     "Return 2-3 sentences, no hype, no invented facts."),
    },
    "topic_classification": {
        "version": 1,
        "template": ("Classify the topic of this text. Creator topics: {topics}.\n"
                     "Text: {text}\n\nRespond with JSON only: "
                     '{"label": "...", "confidence": 0.0-1.0}.'),
    },
    "trend_analysis": {
        "version": 1,
        "template": ("Creator niche: {niche}. Candidate topic: {topic}.\n"
                     "Evidence: {evidence}\n\nIn one sentence, is this a real "
                     "emerging trend? Answer JSON: {\"emerging\": true/false, "
                     "\"reason\": \"...\"}."),
    },
    "content_strategy": {
        "version": 2,
        "template": ("Content brief (JSON): {brief}\n\nWrite the core paragraph "
                     "(120-180 words): one claim, one example, one takeaway. "
                     "Tone: {tone}. No hype, no invented statistics."),
    },
    "linkedin_generation": {
        "version": 1,
        "template": ("Turn this core into a LinkedIn post (Hook -> Context -> "
                     "Insight -> Explanation -> Takeaway -> CTA).\nCore: {core}"),
    },
    "x_generation": {
        "version": 1,
        "template": ("Turn this core into an X thread (strong opening -> concise "
                     "insight -> supporting points, numbered 1/N).\nCore: {core}"),
    },
    "blog_generation": {
        "version": 1,
        "template": ("Turn this core into a blog outline+intro (Title -> Introduction "
                     "-> Sections -> Evidence -> Examples -> Conclusion).\nCore: {core}"),
    },
    "content_critic": {
        "version": 1,
        "template": ("Critique this {platform} draft for: relevance, clarity, "
                     "originality, hook, readability, platform fit, grounding, tone, "
                     "CTA.\nDraft:\n{draft}\n\nRespond with JSON only."),
    },
    "content_revision": {
        "version": 1,
        "template": ("Improve this {platform} draft. Issues: {issues}\n\n"
                     "Draft:\n{draft}\n\nKeep the author's voice. No hype."),
    },
    "insight_generation": {
        "version": 1,
        "template": ("Performance summary: {summary}\n\nWrite 2 durable creator "
                     "insights ('... performs better than ...'). Be specific."),
    },
}

__all__ = ["TEMPLATES", "render"]


def render(name: str, **kwargs) -> str:
    tpl = TEMPLATES[name]
    return tpl["template"].format(**kwargs)


def version(name: str) -> int:
    return TEMPLATES[name]["version"]
