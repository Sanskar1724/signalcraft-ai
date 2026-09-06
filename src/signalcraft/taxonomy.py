"""Audiences + topics taxonomy (§6 entities). Thin helpers over the tables."""
from __future__ import annotations

from .db import get_conn, new_uuid

__all__ = ["list_audiences", "save_audience", "list_topics", "save_topic",
           "sync_profile_taxonomy"]


def list_audiences(user_id: int = 1) -> list[dict]:
    conn = get_conn()
    try:
        return [dict(r) for r in conn.execute(
            "SELECT * FROM audiences WHERE user_id=? ORDER BY name", (user_id,)).fetchall()]
    finally:
        conn.close()


def save_audience(user_id: int, name: str, description: str = "") -> None:
    conn = get_conn()
    try:
        conn.execute(
            "INSERT INTO audiences (uuid, user_id, name, description) VALUES (?,?,?,?)"
            " ON CONFLICT(user_id, name) DO UPDATE SET description=excluded.description",
            (new_uuid(), user_id, name.strip(), description),
        )
        conn.commit()
    finally:
        conn.close()


def list_topics(user_id: int = 1) -> list[dict]:
    conn = get_conn()
    try:
        return [dict(r) for r in conn.execute(
            "SELECT * FROM topics WHERE user_id=? ORDER BY name", (user_id,)).fetchall()]
    finally:
        conn.close()


def save_topic(user_id: int, name: str, status: str = "tracked") -> None:
    conn = get_conn()
    try:
        conn.execute(
            "INSERT INTO topics (uuid, user_id, name, status) VALUES (?,?,?,?)"
            " ON CONFLICT(user_id, name) DO UPDATE SET status=excluded.status",
            (new_uuid(), user_id, name.strip(), status),
        )
        conn.commit()
    finally:
        conn.close()


def sync_profile_taxonomy(user_id: int = 1) -> None:
    """Mirror the profile's audience/topics into the taxonomy tables (§6-§7)."""
    from .profiles import get_profile
    profile = get_profile(user_id)
    if profile.audience:
        save_audience(user_id, profile.audience[:120])
    for t in profile.topics:
        if t.strip():
            save_topic(user_id, t.strip())
    for t in profile.avoid_topics:
        if t.strip():
            save_topic(user_id, t.strip(), status="avoided")
