"""Direct queries the API needs beyond domain helpers (kept in one place, §38.10)."""
from __future__ import annotations

import json

from signalcraft.db import get_conn

__all__ = ["get_content_detail"]


def get_content_detail(content_id: int, user_id: int = 1) -> dict:
    conn = get_conn()
    try:
        row = conn.execute(
            "SELECT c.*, o.topic AS opportunity_topic FROM content c"
            " LEFT JOIN content_opportunities o ON o.id=c.opportunity_id"
            " WHERE c.id=? AND c.user_id=?", (content_id, user_id)).fetchone()
        if row is None:
            raise ValueError(f"content {content_id} not found")
        out = dict(row)
        out["versions"] = [dict(r) for r in conn.execute(
            "SELECT version, score, created_at FROM content_versions"
            " WHERE content_id=? ORDER BY version", (content_id,)).fetchall()]
        perf = conn.execute(
            "SELECT * FROM content_performance WHERE content_id=? ORDER BY id DESC LIMIT 1",
            (content_id,)).fetchone()
        out["performance"] = dict(perf) if perf else {}
        versions_full = conn.execute(
            "SELECT brief FROM content_versions WHERE content_id=? ORDER BY version DESC LIMIT 1",
            (content_id,)).fetchone()
        try:
            out["brief"] = json.loads(versions_full["brief"]) if versions_full else {}
        except Exception:
            out["brief"] = {}
        return out
    finally:
        conn.close()
