"""Research manager (§8-§9): fetch, normalize, dedupe, enrich, store with provenance."""
from __future__ import annotations

import json
import sqlite3

from ..db import get_conn, new_uuid
from ..observability import log
from ..profiles import get_profile
from .base import BaseSource, ResearchItem
from .extra_sources import (
    GitHubSource,
    NewsSource,
    RedditSource,
    SearchTrendsSource,
    WebSearchSource,
    YouTubeSource,
)
from .normalize import normalize_doc
from .rss import RSSSource
from .samples import SampleSource

__all__ = ["collect_and_store", "list_recent", "search"]

SOURCE_TYPES = {"rss": "rss", "sample": "sample", "github": "api", "reddit": "api",
                "youtube": "api", "news": "news", "websearch": "web", "search_trends": "trends"}


def _enrich(it: ResearchItem, profile_keys: set[str]) -> dict:
    from ..trends import freshness_of, tokenize  # lazy: trends imports this package
    toks = tokenize(f"{it.title} {it.summary}")
    overlap = {t for t in toks} & profile_keys
    relevance = round(len(overlap) / max(1, len(set(toks))), 3)
    return {
        "keywords": json.dumps(sorted(set(toks))[:12]),
        "relevance": relevance,
        "freshness": freshness_of(it.published_at),
        "source_type": SOURCE_TYPES.get(it.source, "web"),
    }


def collect_and_store(query: str = "", limit: int = 20, user_id: int = 1,
                      use_live: bool = True, timeout: int = 15) -> list[dict]:
    profile_keys = get_profile(user_id).keywords()
    sources: list[BaseSource] = [SampleSource()]
    if use_live:
        # Pluggable pipeline (§8): new sources append here, no core rewrite.
        sources = [RSSSource(timeout=timeout), GitHubSource(), RedditSource(), YouTubeSource(),
                   NewsSource(), WebSearchSource(), SearchTrendsSource(),
                   SampleSource()]
    seen: dict[str, ResearchItem] = {}
    skipped = 0
    for src in sources:
        try:
            for it in src.fetch(query=query, limit=limit):
                # Normalize at the boundary (§5): raw source output never
                # reaches the database, trends, or content.
                norm = normalize_doc(it.source, it.title, it.summary, it.source_url)
                if norm is None:
                    skipped += 1
                    continue
                key = (norm["source_url"] or "") + "|" + norm["title"].lower()
                if key not in seen:
                    seen[key] = ResearchItem(
                        source=norm["source"], title=norm["title"],
                        summary=norm["summary"], source_url=norm["source_url"],
                        published_at=it.published_at, niche_tags=it.niche_tags)
        except Exception as e:  # §32: continue with available sources
            log.warning("source %s failed: %s", getattr(src, "name", "?"), e)
    if skipped:
        log.info("research normalization skipped %d invalid document(s)", skipped)
    conn = get_conn()
    try:
        for it in list(seen.values())[:limit]:
            try:
                en = _enrich(it, profile_keys)
                conn.execute(
                    "INSERT OR IGNORE INTO research_documents"
                    " (uuid, user_id, source, source_type, source_url, title, summary,"
                    " keywords, topic, published_at, retrieved_at, relevance, freshness,"
                    " niche_tags)"
                    " VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                    (new_uuid(), user_id, it.source, en["source_type"], it.source_url,
                     it.title, it.summary, en["keywords"],
                     (it.niche_tags or [""])[0] if it.niche_tags else "",
                     it.published_at or "", "", en["relevance"], en["freshness"],
                     json.dumps(it.niche_tags or [])),
                )
            except sqlite3.Error as e:
                log.warning("research store failed: %s", e)
        conn.commit()
        rows = conn.execute(
            "SELECT * FROM research_documents WHERE user_id=? ORDER BY id DESC LIMIT ?",
            (user_id, limit),
        ).fetchall()
        stored = [dict(r) for r in rows]
    finally:
        conn.close()
    return stored


def list_recent(user_id: int = 1, limit: int = 30, offset: int = 0) -> list[dict]:
    conn = get_conn()
    try:
        rows = conn.execute(
            "SELECT * FROM research_documents WHERE user_id=? ORDER BY id DESC LIMIT ? OFFSET ?",
            (user_id, limit, offset),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def search(user_id: int = 1, query: str = "", limit: int = 20, offset: int = 0) -> list[dict]:
    conn = get_conn()
    try:
        rows = conn.execute(
            "SELECT * FROM research_documents WHERE user_id=? AND (title LIKE ? OR summary LIKE ?)"
            " ORDER BY id DESC LIMIT ? OFFSET ?",
            (user_id, f"%{query}%", f"%{query}%", limit, offset),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()
