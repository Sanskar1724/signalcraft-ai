"""Content calendar helpers (§20)."""
from __future__ import annotations

from .db import get_conn, new_uuid

__all__ = [
    "CALENDAR_STATUSES",
    "duplicate_entry",
    "schedule",
    "upcoming",
    "update_entry",
]

CALENDAR_STATUSES = {"draft", "scheduled", "published", "cancelled"}


def schedule(user_id: int, platform: str, scheduled_for: str,
             content_id: int | None = None, notes: str = "") -> dict:
    conn = get_conn()
    try:
        cur = conn.execute(
            "INSERT INTO calendar_items (uuid, user_id, content_id, platform, scheduled_for, notes)"
            " VALUES (?,?,?,?,?,?)", (new_uuid(), user_id, content_id, platform, scheduled_for, notes[:500]),
        )
        conn.commit()
        row = conn.execute("SELECT * FROM calendar_items WHERE id=?", (cur.lastrowid,)).fetchone()
        return dict(row)
    finally:
        conn.close()


def upcoming(user_id: int = 1, limit: int = 30) -> list[dict]:
    conn = get_conn()
    try:
        rows = conn.execute(
            "SELECT e.*, c.title FROM calendar_items e LEFT JOIN content c ON c.id=e.content_id"
            " WHERE e.user_id=? ORDER BY e.scheduled_for LIMIT ?", (user_id, limit)).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def update_entry(entry_id: int, user_id: int = 1, **fields) -> dict:
    allowed = {"platform", "scheduled_for", "status", "notes", "content_id"}
    updates = {k: v for k, v in fields.items() if k in allowed and v is not None}
    if "status" in updates and updates["status"] not in CALENDAR_STATUSES:
        raise ValueError(f"invalid status: {updates['status']}")
    if "notes" in updates:
        updates["notes"] = str(updates["notes"])[:500]
    conn = get_conn()
    try:
        row = conn.execute("SELECT id FROM calendar_items WHERE id=? AND user_id=?",
                           (entry_id, user_id)).fetchone()
        if row is None:
            raise ValueError(f"calendar entry {entry_id} not found")
        if updates:
            sets = ", ".join(f"{k}=?" for k in updates)
            conn.execute(f"UPDATE calendar_items SET {sets} WHERE id=?",
                         (*updates.values(), entry_id))
            conn.commit()
        return dict(conn.execute("SELECT * FROM calendar_items WHERE id=?",
                                 (entry_id,)).fetchone())
    finally:
        conn.close()


def duplicate_entry(entry_id: int, user_id: int = 1) -> dict:
    conn = get_conn()
    try:
        row = conn.execute("SELECT * FROM calendar_items WHERE id=? AND user_id=?",
                           (entry_id, user_id)).fetchone()
        if row is None:
            raise ValueError(f"calendar entry {entry_id} not found")
        src = dict(row)
        cur = conn.execute(
            "INSERT INTO calendar_items (uuid, user_id, content_id, platform,"
            " scheduled_for, status, notes) VALUES (?,?,?,?,?,'draft',?)",
            (new_uuid(), user_id, src["content_id"], src["platform"],
             src["scheduled_for"], (src["notes"] or "")[:490] + " (copy)"),
        )
        conn.commit()
        return dict(conn.execute("SELECT * FROM calendar_items WHERE id=?",
                                 (cur.lastrowid,)).fetchone())
    finally:
        conn.close()
