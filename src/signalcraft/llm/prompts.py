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
        "version": 3,
        "template": ("Content brief (JSON): {brief}\n\nWrite the core paragraph "
                     "(120-180 words) a working creator would actually post:\n"
                     "1. Open with a sharp, specific hook — no throat-clearing.\n"
                     "2. One claim, one concrete example, one takeaway.\n"
                     "3. Use ONLY the facts in supporting_evidence; never invent "
                     "statistics, quotes, URLs or events. If evidence is thin, say "
                     "what you observed, not what you assume.\n"
                     "4. Match the voice in style_reference when present; ignore "
                     "it when empty.\n"
                     "5. Banned phrases: game-changer, revolutionize, unlock the "
                     "power, in today's fast-paced world, delving into.\n"
                     "Tone: {tone}."),
    },
    "linkedin_generation": {
        "version": 3,
        "template": ("{brief_prose}\n\nWrite ONLY the finished LinkedIn post, nothing else — "
                     "Hook (one sharp line) -> Context (2-3 lines) -> Insight -> "
                     "Short explanation -> Takeaway -> CTA question.\n"
                     "Tone: {tone}."),
    },
    "x_generation": {
        "version": 3,
        "template": ("{brief_prose}\n\nWrite ONLY the finished X thread, nothing else — "
                     "Numbered posts (1/N format). Post 1: strong opening under 240 "
                     "characters. Then concise insight plus supporting points. Final "
                     "post: one takeaway.\n"
                     "Tone: {tone}."),
    },
    "blog_generation": {
        "version": 3,
        "template": ("{brief_prose}\n\nWrite ONLY the finished blog article, nothing else — "
                     "Markdown Title -> Introduction -> sections with ## headers -> "
                     "Evidence -> Examples -> Conclusion.\n"
                     "Tone: {tone}."),
    },
    "newsletter_generation": {
        "version": 2,
        "template": ("{brief_prose}\n\nWrite ONLY the finished newsletter issue, nothing else — "
                     "Subject line first, then greeting, one insight with an example, "
                     "one thing to try, and a reply-style CTA.\n"
                     "Tone: {tone}."),
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
