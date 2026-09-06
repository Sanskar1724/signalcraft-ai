"""Creator memory (§14): structured, selective — not every interaction.

Kinds: successful_topic, weak_topic, successful_hook, weak_hook,
preferred_format, audience_pattern, user_feedback, strategy_insight.
Semantic recall uses the local hash embedding (no extra dependency);
a real vector store can replace it later without changing callers.
"""
from __future__ import annotations

from .db import get_conn

VALID_KINDS = {"successful_topic", "weak_topic", "successful_hook", "weak_hook",
               "preferred_format", "audience_pattern", "user_feedback",
               "strategy_insight"}


def remember(user_id: int, kind: str, key: str, value: str, confidence: float = 0.6) -> None:
    if kind not in VALID_KINDS:
        raise ValueError(f"invalid memory kind: {kind}")
    if not key or not key.strip():
        raise ValueError("memory key must be non-empty")
    key = key.strip()[:120]
    conn = get_conn()
    try:
        conn.execute(
            "INSERT INTO memories (user_id, kind, key, value, confidence, hits)"
            " VALUES (?,?,?,?,?,1)"
            " ON CONFLICT(user_id, kind, key) DO UPDATE SET"
            " value=excluded.value, confidence=excluded.confidence,"
            " hits=hits+1, updated_at=datetime('now')",
            (user_id, kind, key, value, confidence),
        )
        conn.commit()
    finally:
        conn.close()


def recall(user_id: int = 1, kind: str | None = None, limit: int = 50) -> list[dict]:
    conn = get_conn()
    try:
        if kind:
            rows = conn.execute(
                "SELECT * FROM memories WHERE user_id=? AND kind=? ORDER BY hits DESC LIMIT ?",
                (user_id, kind, limit)).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM memories WHERE user_id=? ORDER BY hits DESC LIMIT ?",
                (user_id, limit)).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_memory_boost(user_id: int, topic: str) -> float:
    """Adjust opportunity score from past learnings. Bounded [-8, +8]."""
    t = topic.lower()
    boost = 0.0
    for m in recall(user_id, limit=100):
        k = m["kind"]
        key = m["key"].lower()
        if k == "successful_topic" and (key in t or t in key):
            boost += 4.0 * m["confidence"]
        elif k == "weak_topic" and (key in t or t in key):
            boost -= 4.0 * m["confidence"]
        elif k == "preferred_format" and key in t:
            boost += 1.5
        elif k == "strategy_insight" and (key in t or t in key):
            boost += 1.0 * m["confidence"]
    return max(-8.0, min(8.0, boost))


def semantic_recall(user_id: int, query: str, limit: int = 5) -> list[dict]:
    """Rank memories by cosine similarity to the query using local embeddings."""
    from .llm import LLMGateway
    gateway = LLMGateway()
    q = gateway.embed(query)
    scored = []
    for m in recall(user_id, limit=100):
        v = gateway.embed(f"{m['key']} {m['value']}")
        sim = sum(a * b for a, b in zip(q, v))
        scored.append((sim, m))
    scored.sort(key=lambda p: p[0], reverse=True)
    return [m for _, m in scored[:limit]]


def remember_feedback(user_id: int, topic: str, liked: bool, note: str = "") -> None:
    """Store explicit user feedback (§14): liked/disliked content direction."""
    kind = "successful_topic" if liked else "weak_topic"
    remember(user_id, kind, topic.lower()[:80], note or ("liked" if liked else "disliked"), 0.8)
    remember(user_id, "user_feedback", topic.lower()[:80],
             note or ("liked" if liked else "disliked"), 0.8)


def learn_from_performance(user_id: int = 1) -> list[str]:
    """Derive durable insights from analytics. Returns human-readable notes."""
    from .analytics import summary
    s = summary(user_id)
    notes = []
    for t in (s.get("best_topics") or [])[:3]:
        remember(user_id, "successful_topic", str(t["topic"]).lower()[:80],
                 f"Engagement {t.get('avg_engagement')}", 0.7)
        notes.append(f"Strong topic: {t['topic']}")
    for t in (s.get("weak_topics") or [])[:3]:
        remember(user_id, "weak_topic", str(t["topic"]).lower()[:80],
                 f"Engagement {t.get('avg_engagement')}", 0.6)
        notes.append(f"Weak topic: {t['topic']}")
    for h in (s.get("best_hooks") or [])[:2]:
        if h.get("hook"):
            remember(user_id, "successful_hook", str(h["hook"])[:80],
                     f"Engagement {h.get('avg_engagement')}", 0.6)
            notes.append(f"Strong hook: {str(h['hook'])[:60]}")
    for p in (s.get("best_formats") or [])[:1]:
        remember(user_id, "preferred_format", str(p.get("platform", ""))[:80],
                 f"Engagement {p.get('avg_engagement')}", 0.6)
    return notes
