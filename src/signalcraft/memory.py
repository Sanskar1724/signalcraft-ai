"""Creator memory: structured, selective — not every interaction."""
from __future__ import annotations

from .db import get_conn


def remember(user_id: int, kind: str, key: str, value: str, confidence: float = 0.6) -> None:
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
    return max(-8.0, min(8.0, boost))


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
    return notes
