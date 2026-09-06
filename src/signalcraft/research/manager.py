"""Research manager: fetch from sources, dedupe, store with provenance."""
from __future__ import annotations

import json
import sqlite3

from ..db import get_conn
from ..observability import log
from .base import BaseSource, ResearchItem
from .rss import RSSSource
from .samples import SampleSource


def collect_and_store(query: str = "", limit: int = 20, user_id: int = 1,
                      use_live: bool = True) -> list[dict]:
    sources: list[BaseSource] = [SampleSource()]
    if use_live:
        sources.insert(0, RSSSource())
    seen: dict[str, ResearchItem] = {}
    for src in sources:
        try:
            for it in src.fetch(query=query, limit=limit):
                key = (it.source_url or "") + "|" + it.title
                if key not in seen:
                    seen[key] = it
        except Exception as e:
            log.warning("source %s failed: %s", getattr(src, "name", "?"), e)
    stored = []
    conn = get_conn()
    try:
        for it in list(seen.values())[:limit]:
            try:
                conn.execute(
                    "INSERT OR IGNORE INTO research_items"
                    " (user_id, source, source_url, title, summary, published_at, niche_tags)"
                    " VALUES (?,?,?,?,?,?,?)",
                    (user_id, it.source, it.source_url, it.title, it.summary,
                     it.published_at or "", json.dumps(it.niche_tags or [])),
                )
            except sqlite3.Error as e:
                log.warning("research store failed: %s", e)
        conn.commit()
        rows = conn.execute(
            "SELECT * FROM research_items WHERE user_id=? ORDER BY id DESC LIMIT ?",
            (user_id, limit),
        ).fetchall()
        stored = [dict(r) for r in rows]
    finally:
        conn.close()
    return stored


def list_recent(user_id: int = 1, limit: int = 30) -> list[dict]:
    conn = get_conn()
    try:
        rows = conn.execute(
            "SELECT * FROM research_items WHERE user_id=? ORDER BY id DESC LIMIT ?",
            (user_id, limit),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def search(user_id: int = 1, query: str = "", limit: int = 20) -> list[dict]:
    conn = get_conn()
    try:
        rows = conn.execute(
            "SELECT * FROM research_items WHERE user_id=? AND (title LIKE ? OR summary LIKE ?)"
            " ORDER BY id DESC LIMIT ?",
            (user_id, f"%{query}%", f"%{query}%", limit),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()
