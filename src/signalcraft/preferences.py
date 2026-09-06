"""User preferences (§15): content, platform and AI-behavior controls.

Structured table (queried often); formats stay JSON (genuinely flexible, §12).
"""
from __future__ import annotations

import json

from .db import get_conn, new_uuid

__all__ = ["DEFAULT_PREFS", "get_preferences", "update_preferences"]

DEFAULT_PREFS = {
    "tone": "", "length": "medium", "creativity": 0.7, "research_depth": "standard",
    "use_trends": 1, "always_research": 1, "citation_pref": "link",
    "emoji_pref": "none", "cta_pref": "question", "formality": "neutral",
    "sentence_style": "", "formats": [], "frequency": "flexible",
}

_COLUMNS = ("tone", "length", "creativity", "research_depth", "use_trends",
            "always_research", "citation_pref", "emoji_pref", "cta_pref",
            "formality", "sentence_style", "formats", "frequency")


def get_preferences(user_id: int = 1) -> dict:
    conn = get_conn()
    try:
        row = conn.execute("SELECT * FROM preferences WHERE user_id=?", (user_id,)).fetchone()
        if row is None:
            conn.execute("INSERT INTO preferences (uuid, user_id) VALUES (?, ?)",
                         (new_uuid(), user_id))
            conn.commit()
            row = conn.execute("SELECT * FROM preferences WHERE user_id=?", (user_id,)).fetchone()
        out = dict(row)
        try:
            out["formats"] = json.loads(out.get("formats") or "[]")
        except Exception:
            out["formats"] = []
        return out
    finally:
        conn.close()


def update_preferences(user_id: int = 1, **fields) -> dict:
    updates = {}
    for k, v in fields.items():
        if k not in _COLUMNS or v is None:
            if k not in _COLUMNS and v is not None:
                raise ValueError(f"invalid preference: {k}")
            continue
        if k == "formats" and isinstance(v, list):
            v = json.dumps(v)
        if k in {"use_trends", "always_research"}:
            v = int(bool(v))
        if k == "creativity":
            v = max(0.0, min(1.0, float(v)))
        updates[k] = v
    if updates:
        conn = get_conn()
        try:
            get_preferences(user_id)  # ensure row exists (separate conn, committed)
            sets = ", ".join(f"{k}=?" for k in updates)
            conn.execute(f"UPDATE preferences SET {sets}, updated_at=datetime('now')"
                         " WHERE user_id=?", (*updates.values(), user_id))
            conn.commit()
        finally:
            conn.close()
    return get_preferences(user_id)
