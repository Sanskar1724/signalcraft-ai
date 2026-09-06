# Database (§20)

SQLite WAL at `data/signalcraft.db` (see `src/signalcraft/db.py`).
`init_db()` creates the schema and applies additive `ALTER TABLE`
migrations for older dev databases.

Tables: `users`, `profiles` (12 fields: niche, expertise, audience, goals,
platforms, writing style/tone, topics, avoid_topics, content_preferences,
posting_preferences, style_notes), `audiences`, `topics`, `research_items`
(with `source` + `source_url` provenance), `trends` (7 scored dimensions +
evidence), `opportunities`, `recommendations` (ranked snapshot per run),
`content_items`, `content_versions`, `performance` (incl. `reach` +
`engagement_rate`), `calendar_entries`, `memories`, `llm_requests`.

Vector search is intentionally not a table: `LLMGateway.embed()` gives
local hash embeddings for `memory.semantic_recall()`; swap in pgvector
later without changing callers.
