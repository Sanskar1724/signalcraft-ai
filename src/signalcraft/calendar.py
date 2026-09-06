"""Content calendar helpers (§20)."""
from __future__ import annotations

from .db import get_conn

__all__ = ["schedule", "upcoming"]


def schedule(user_id: int, platform: str, scheduled_for: str,
             content_id: int | None = None, notes: str = "") -> dict:
    conn = get_conn()
    try:
        cur = conn.execute(
            "INSERT INTO calendar_entries (user_id, content_id, platform, scheduled_for, notes)"
            " VALUES (?,?,?,?,?)", (user_id, content_id, platform, scheduled_for, notes[:500]),
        )
        conn.commit()
        row = conn.execute("SELECT * FROM calendar_entries WHERE id=?", (cur.lastrowid,)).fetchone()
        return dict(row)
    finally:
        conn.close()


def upcoming(user_id: int = 1, limit: int = 30) -> list[dict]:
    conn = get_conn()
    try:
        rows = conn.execute(
            "SELECT e.*, c.title FROM calendar_entries e LEFT JOIN content_items c ON c.id=e.content_id"
            " WHERE e.user_id=? ORDER BY e.scheduled_for LIMIT ?", (user_id, limit)).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()
