"""SQLite source of truth (§6 entities, UUIDs, timestamps, indexes, migrations).

Entity names follow prompt1 §6: users, profiles, audiences, topics,
research_documents, trend_signals, content_opportunities, recommendations,
content, content_versions, content_performance, calendar_items,
agent_memories, llm_requests.
"""
from __future__ import annotations

import sqlite3
import uuid as _uuid
from pathlib import Path

from .config import settings

__all__ = ["SCHEMA", "get_conn", "init_db", "new_uuid"]


def new_uuid() -> str:
    return str(_uuid.uuid4())


SCHEMA = """
PRAGMA journal_mode=WAL;

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    uuid TEXT NOT NULL DEFAULT '',
    name TEXT NOT NULL DEFAULT 'Creator',
    email TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    uuid TEXT NOT NULL DEFAULT '',
    user_id INTEGER NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    niche TEXT NOT NULL DEFAULT '',
    expertise TEXT NOT NULL DEFAULT '',
    expertise_level TEXT NOT NULL DEFAULT '',
    audience TEXT NOT NULL DEFAULT '',
    goals TEXT NOT NULL DEFAULT '',
    platforms TEXT NOT NULL DEFAULT '["LinkedIn","X","Blog"]',
    writing_style TEXT NOT NULL DEFAULT '',
    tone TEXT NOT NULL DEFAULT '',
    topics TEXT NOT NULL DEFAULT '[]',
    avoid_topics TEXT NOT NULL DEFAULT '[]',
    style_notes TEXT NOT NULL DEFAULT '',
    content_preferences TEXT NOT NULL DEFAULT '',
    posting_preferences TEXT NOT NULL DEFAULT '',
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS audiences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    uuid TEXT NOT NULL DEFAULT '',
    user_id INTEGER NOT NULL DEFAULT 1 REFERENCES users(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE(user_id, name)
);

CREATE TABLE IF NOT EXISTS topics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    uuid TEXT NOT NULL DEFAULT '',
    user_id INTEGER NOT NULL DEFAULT 1 REFERENCES users(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'tracked',
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE(user_id, name)
);

CREATE TABLE IF NOT EXISTS research_documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    uuid TEXT NOT NULL DEFAULT '',
    user_id INTEGER NOT NULL DEFAULT 1,
    source TEXT NOT NULL,
    source_type TEXT NOT NULL DEFAULT 'rss',
    source_url TEXT NOT NULL DEFAULT '',
    title TEXT NOT NULL,
    summary TEXT NOT NULL DEFAULT '',
    keywords TEXT NOT NULL DEFAULT '[]',
    topic TEXT NOT NULL DEFAULT '',
    published_at TEXT NOT NULL DEFAULT (datetime('now')),
    retrieved_at TEXT NOT NULL DEFAULT (datetime('now')),
    relevance REAL NOT NULL DEFAULT 0,
    freshness REAL NOT NULL DEFAULT 0,
    niche_tags TEXT NOT NULL DEFAULT '[]',
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE(source, source_url, title)
);

CREATE TABLE IF NOT EXISTS trend_signals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    uuid TEXT NOT NULL DEFAULT '',
    user_id INTEGER NOT NULL DEFAULT 1,
    topic TEXT NOT NULL,
    freshness REAL NOT NULL DEFAULT 0,
    growth REAL NOT NULL DEFAULT 0,
    relevance REAL NOT NULL DEFAULT 0,
    source_momentum REAL NOT NULL DEFAULT 0,
    novelty REAL NOT NULL DEFAULT 0,
    audience_fit REAL NOT NULL DEFAULT 0,
    competition REAL NOT NULL DEFAULT 0,
    trend_score REAL NOT NULL DEFAULT 0,
    evidence TEXT NOT NULL DEFAULT '[]',
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS content_opportunities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    uuid TEXT NOT NULL DEFAULT '',
    user_id INTEGER NOT NULL DEFAULT 1,
    topic TEXT NOT NULL,
    trend_score REAL NOT NULL DEFAULT 0,
    user_relevance REAL NOT NULL DEFAULT 0,
    audience_fit REAL NOT NULL DEFAULT 0,
    freshness REAL NOT NULL DEFAULT 0,
    competition REAL NOT NULL DEFAULT 0,
    why_now TEXT NOT NULL DEFAULT '',
    why_you TEXT NOT NULL DEFAULT '',
    audience TEXT NOT NULL DEFAULT '',
    angle TEXT NOT NULL DEFAULT '',
    format TEXT NOT NULL DEFAULT '',
    platform TEXT NOT NULL DEFAULT '',
    score REAL NOT NULL DEFAULT 0,
    confidence REAL NOT NULL DEFAULT 0,
    research_refs TEXT NOT NULL DEFAULT '[]',
    status TEXT NOT NULL DEFAULT 'new',
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS content (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    uuid TEXT NOT NULL DEFAULT '',
    user_id INTEGER NOT NULL DEFAULT 1,
    opportunity_id INTEGER REFERENCES content_opportunities(id) ON DELETE SET NULL,
    platform TEXT NOT NULL,
    title TEXT NOT NULL DEFAULT '',
    body TEXT NOT NULL,
    hook TEXT NOT NULL DEFAULT '',
    cta TEXT NOT NULL DEFAULT '',
    quality_score REAL NOT NULL DEFAULT 0,
    status TEXT NOT NULL DEFAULT 'draft',
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS content_versions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    uuid TEXT NOT NULL DEFAULT '',
    content_id INTEGER NOT NULL REFERENCES content(id) ON DELETE CASCADE,
    version INTEGER NOT NULL,
    brief TEXT NOT NULL DEFAULT '{}',
    body TEXT NOT NULL,
    critique TEXT NOT NULL DEFAULT '',
    score REAL NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS content_performance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    uuid TEXT NOT NULL DEFAULT '',
    content_id INTEGER NOT NULL REFERENCES content(id) ON DELETE CASCADE,
    platform TEXT NOT NULL DEFAULT '',
    impressions INTEGER NOT NULL DEFAULT 0,
    likes INTEGER NOT NULL DEFAULT 0,
    comments INTEGER NOT NULL DEFAULT 0,
    shares INTEGER NOT NULL DEFAULT 0,
    clicks INTEGER NOT NULL DEFAULT 0,
    saves INTEGER NOT NULL DEFAULT 0,
    reach INTEGER NOT NULL DEFAULT 0,
    engagement_rate REAL NOT NULL DEFAULT 0,
    performance_score REAL NOT NULL DEFAULT 0,
    recorded_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS agent_memories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    uuid TEXT NOT NULL DEFAULT '',
    user_id INTEGER NOT NULL DEFAULT 1,
    kind TEXT NOT NULL,
    key TEXT NOT NULL,
    value TEXT NOT NULL,
    confidence REAL NOT NULL DEFAULT 0.5,
    hits INTEGER NOT NULL DEFAULT 1,
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE(user_id, kind, key)
);

CREATE TABLE IF NOT EXISTS llm_requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    uuid TEXT NOT NULL DEFAULT '',
    provider TEXT NOT NULL,
    model TEXT NOT NULL,
    task TEXT NOT NULL DEFAULT '',
    latency_ms INTEGER NOT NULL DEFAULT 0,
    prompt_tokens INTEGER NOT NULL DEFAULT 0,
    completion_tokens INTEGER NOT NULL DEFAULT 0,
    cost_usd REAL NOT NULL DEFAULT 0,
    success INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS calendar_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    uuid TEXT NOT NULL DEFAULT '',
    user_id INTEGER NOT NULL DEFAULT 1,
    content_id INTEGER REFERENCES content(id) ON DELETE SET NULL,
    platform TEXT NOT NULL DEFAULT '',
    scheduled_for TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'draft',
    notes TEXT NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS recommendations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    uuid TEXT NOT NULL DEFAULT '',
    user_id INTEGER NOT NULL DEFAULT 1 REFERENCES users(id) ON DELETE CASCADE,
    opportunity_id INTEGER REFERENCES content_opportunities(id) ON DELETE SET NULL,
    reason TEXT NOT NULL DEFAULT '',
    rank INTEGER NOT NULL DEFAULT 0,
    status TEXT NOT NULL DEFAULT 'suggested',
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_research_user ON research_documents(user_id);
CREATE INDEX IF NOT EXISTS idx_trends_user ON trend_signals(user_id);
CREATE INDEX IF NOT EXISTS idx_opps_user ON content_opportunities(user_id);
CREATE INDEX IF NOT EXISTS idx_content_user ON content(user_id);
CREATE INDEX IF NOT EXISTS idx_perf_content ON content_performance(content_id);
CREATE INDEX IF NOT EXISTS idx_mem_user ON agent_memories(user_id);
CREATE INDEX IF NOT EXISTS idx_llm_task ON llm_requests(task);
"""

# Legacy (pre-prompt1) table names -> §6 names.
LEGACY_RENAMES = {
    "research_items": "research_documents",
    "trends": "trend_signals",
    "opportunities": "content_opportunities",
    "content_items": "content",
    "performance": "content_performance",
    "memories": "agent_memories",
    "calendar_entries": "calendar_items",
}

# Columns that may be missing on renamed tables (name -> DDL).
EXTRA_COLUMNS: dict[str, list[str]] = {
    "research_documents": [
        "uuid TEXT NOT NULL DEFAULT ''", "source_type TEXT NOT NULL DEFAULT 'rss'",
        "keywords TEXT NOT NULL DEFAULT '[]'", "topic TEXT NOT NULL DEFAULT ''",
        "retrieved_at TEXT NOT NULL DEFAULT (datetime('now'))",
        "relevance REAL NOT NULL DEFAULT 0", "freshness REAL NOT NULL DEFAULT 0",
    ],
    "trend_signals": [
        "uuid TEXT NOT NULL DEFAULT ''", "source_momentum REAL NOT NULL DEFAULT 0",
        "audience_fit REAL NOT NULL DEFAULT 0", "competition REAL NOT NULL DEFAULT 0",
        "trend_score REAL NOT NULL DEFAULT 0",
    ],
    "content_opportunities": [
        "uuid TEXT NOT NULL DEFAULT ''", "trend_score REAL NOT NULL DEFAULT 0",
        "user_relevance REAL NOT NULL DEFAULT 0", "audience_fit REAL NOT NULL DEFAULT 0",
        "freshness REAL NOT NULL DEFAULT 0", "competition REAL NOT NULL DEFAULT 0",
    ],
    "content": ["uuid TEXT NOT NULL DEFAULT ''", "status TEXT NOT NULL DEFAULT 'draft'"],
    "content_versions": ["uuid TEXT NOT NULL DEFAULT ''", "brief TEXT NOT NULL DEFAULT '{}'"],
    "content_performance": ["uuid TEXT NOT NULL DEFAULT ''", "performance_score REAL NOT NULL DEFAULT 0"],
    "agent_memories": ["uuid TEXT NOT NULL DEFAULT ''"],
    "calendar_items": ["uuid TEXT NOT NULL DEFAULT ''"],
    "llm_requests": ["uuid TEXT NOT NULL DEFAULT ''"],
    "users": ["uuid TEXT NOT NULL DEFAULT ''"],
    "profiles": [
        "uuid TEXT NOT NULL DEFAULT ''", "expertise_level TEXT NOT NULL DEFAULT ''",
        "writing_style TEXT NOT NULL DEFAULT ''", "content_preferences TEXT NOT NULL DEFAULT ''",
        "posting_preferences TEXT NOT NULL DEFAULT ''",
    ],
    "recommendations": ["uuid TEXT NOT NULL DEFAULT ''"],
}


def _tables(conn: sqlite3.Connection) -> set[str]:
    return {r[0] for r in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table'").fetchall()}


def _backfill_uuids(conn: sqlite3.Connection) -> None:
    for (table,) in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
            " AND sql LIKE '%uuid TEXT%'").fetchall():
        rows = conn.execute(f"SELECT id FROM {table} WHERE uuid=''").fetchall()
        for (rid,) in rows:
            conn.execute(f"UPDATE {table} SET uuid=? WHERE id=?", (new_uuid(), rid))


def _migrate(conn: sqlite3.Connection) -> None:
    """Rename legacy tables, add §6 columns, backfill UUIDs."""
    tables = _tables(conn)
    for old, new in LEGACY_RENAMES.items():
        if old in tables and new not in tables:
            conn.execute(f"ALTER TABLE {old} RENAME TO {new}")
    # content_versions.score already exists from earlier MVP; keep.
    for table, ddls in EXTRA_COLUMNS.items():
        existing = {r["name"] for r in conn.execute(f"PRAGMA table_info({table})").fetchall()}
        for ddl in ddls:
            col = ddl.split()[0]
            if col not in existing:
                conn.execute(f"ALTER TABLE {table} ADD COLUMN {ddl}")
    _backfill_uuids(conn)
    # recommendations created pre-prompt1 references the old opportunities table.
    rec = conn.execute(
        "SELECT sql FROM sqlite_master WHERE name='recommendations'").fetchone()
    if rec and "REFERENCES opportunities(" in (rec[0] or ""):
        conn.execute("DROP TABLE recommendations")
        conn.execute("""
        CREATE TABLE recommendations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            uuid TEXT NOT NULL DEFAULT '',
            user_id INTEGER NOT NULL DEFAULT 1 REFERENCES users(id) ON DELETE CASCADE,
            opportunity_id INTEGER REFERENCES content_opportunities(id) ON DELETE SET NULL,
            reason TEXT NOT NULL DEFAULT '',
            rank INTEGER NOT NULL DEFAULT 0,
            status TEXT NOT NULL DEFAULT 'suggested',
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        )""")
        _backfill_uuids(conn)


def get_conn(db_path: Path | None = None) -> sqlite3.Connection:
    path = Path(db_path) if db_path else settings.db_path
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db(db_path: Path | None = None) -> Path:
    path = Path(db_path) if db_path else settings.db_path
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = get_conn(path)
    try:
        conn.executescript(SCHEMA)
        _migrate(conn)
        row = conn.execute("SELECT id FROM users WHERE id=1").fetchone()
        if row is None:
            conn.execute("INSERT INTO users (id, uuid, name) VALUES (1, ?, 'Creator')",
                         (new_uuid(),))
            conn.execute("INSERT INTO profiles (uuid, user_id) VALUES (?, 1)", (new_uuid(),))
            conn.commit()
    finally:
        conn.close()
    return path
