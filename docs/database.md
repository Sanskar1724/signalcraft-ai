# Database (§6)

SQLite at `data/signalcraft.db` (`src/signalcraft/db.py`). Tables: `users`,
`profiles` (14 fields incl. expertise_level, writing_style, content/posting
preferences), `audiences`, `topics`, `research_documents` (source, source_type,
URL, keywords, topic, published/retrieved dates, relevance, freshness),
`trend_signals` (7 signals + `trend_score`), `content_opportunities`
(trend_score, user_relevance, audience_fit, freshness, competition, `score`,
confidence, research_refs), `recommendations` (ranked snapshot), `content`
(+ `status` draft/published), `content_versions` (+ validated `brief`),
`content_performance` (+ `reach`, `engagement_rate`, `performance_score`),
`calendar_items`, `agent_memories`, `llm_requests` (+ `cost_usd`).

Every row carries a `uuid` (Python-generated, backfilled by migration) and
timestamps; FK indexes exist (`idx_*`). `init_db()` creates the schema and
applies `_migrate()` (pre-prompt1 renames + additive columns); the same steps
are kept as SQL in `apps/api/migrations/` for review.

Postgres/pgvector + Redis cutover: `docker-compose.yml` provisions
`postgres` (pgvector image) and `redis`; `DATABASE_URL`/`REDIS_URL` are
reserved in `.env.example`. The cutover means translating `SCHEMA` types,
enabling pgvector for `memory.semantic_recall()`, and moving `jobs` onto a
worker — no domain-logic rewrite.
