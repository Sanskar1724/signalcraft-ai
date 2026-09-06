-- 0002: prompt1 §6 renames + UUID/timestamp/index columns.
-- Applied automatically by signalcraft.db._migrate() for SQLite dev DBs.
-- Kept as SQL for review and for the Postgres cutover (translate types).

ALTER TABLE research_items RENAME TO research_documents;
ALTER TABLE trends RENAME TO trend_signals;
ALTER TABLE opportunities RENAME TO content_opportunities;
ALTER TABLE content_items RENAME TO content;
ALTER TABLE performance RENAME TO content_performance;
ALTER TABLE memories RENAME TO agent_memories;
ALTER TABLE calendar_entries RENAME TO calendar_items;

ALTER TABLE research_documents ADD COLUMN uuid TEXT NOT NULL DEFAULT '';
ALTER TABLE research_documents ADD COLUMN source_type TEXT NOT NULL DEFAULT 'rss';
ALTER TABLE research_documents ADD COLUMN keywords TEXT NOT NULL DEFAULT '[]';
ALTER TABLE research_documents ADD COLUMN topic TEXT NOT NULL DEFAULT '';
ALTER TABLE research_documents ADD COLUMN retrieved_at TEXT NOT NULL DEFAULT (datetime('now'));
ALTER TABLE research_documents ADD COLUMN relevance REAL NOT NULL DEFAULT 0;
ALTER TABLE research_documents ADD COLUMN freshness REAL NOT NULL DEFAULT 0;

ALTER TABLE trend_signals ADD COLUMN uuid TEXT NOT NULL DEFAULT '';
ALTER TABLE trend_signals ADD COLUMN source_momentum REAL NOT NULL DEFAULT 0;
ALTER TABLE trend_signals ADD COLUMN audience_fit REAL NOT NULL DEFAULT 0;
ALTER TABLE trend_signals ADD COLUMN competition REAL NOT NULL DEFAULT 0;
ALTER TABLE trend_signals ADD COLUMN trend_score REAL NOT NULL DEFAULT 0;

ALTER TABLE content_opportunities ADD COLUMN uuid TEXT NOT NULL DEFAULT '';
ALTER TABLE content_opportunities ADD COLUMN trend_score REAL NOT NULL DEFAULT 0;
ALTER TABLE content_opportunities ADD COLUMN user_relevance REAL NOT NULL DEFAULT 0;
ALTER TABLE content_opportunities ADD COLUMN audience_fit REAL NOT NULL DEFAULT 0;
ALTER TABLE content_opportunities ADD COLUMN freshness REAL NOT NULL DEFAULT 0;
ALTER TABLE content_opportunities ADD COLUMN competition REAL NOT NULL DEFAULT 0;

ALTER TABLE content ADD COLUMN uuid TEXT NOT NULL DEFAULT '';
ALTER TABLE content ADD COLUMN status TEXT NOT NULL DEFAULT 'draft';
ALTER TABLE content_versions ADD COLUMN uuid TEXT NOT NULL DEFAULT '';
ALTER TABLE content_versions ADD COLUMN brief TEXT NOT NULL DEFAULT '{}';
ALTER TABLE content_performance ADD COLUMN uuid TEXT NOT NULL DEFAULT '';
ALTER TABLE content_performance ADD COLUMN performance_score REAL NOT NULL DEFAULT 0;
ALTER TABLE agent_memories ADD COLUMN uuid TEXT NOT NULL DEFAULT '';
ALTER TABLE calendar_items ADD COLUMN uuid TEXT NOT NULL DEFAULT '';
ALTER TABLE llm_requests ADD COLUMN uuid TEXT NOT NULL DEFAULT '';
ALTER TABLE users ADD COLUMN uuid TEXT NOT NULL DEFAULT '';
ALTER TABLE profiles ADD COLUMN uuid TEXT NOT NULL DEFAULT '';
ALTER TABLE profiles ADD COLUMN expertise_level TEXT NOT NULL DEFAULT '';
ALTER TABLE profiles ADD COLUMN writing_style TEXT NOT NULL DEFAULT '';
ALTER TABLE profiles ADD COLUMN content_preferences TEXT NOT NULL DEFAULT '';
ALTER TABLE profiles ADD COLUMN posting_preferences TEXT NOT NULL DEFAULT '';

CREATE INDEX IF NOT EXISTS idx_research_user ON research_documents(user_id);
CREATE INDEX IF NOT EXISTS idx_trends_user ON trend_signals(user_id);
CREATE INDEX IF NOT EXISTS idx_opps_user ON content_opportunities(user_id);
CREATE INDEX IF NOT EXISTS idx_content_user ON content(user_id);
CREATE INDEX IF NOT EXISTS idx_perf_content ON content_performance(content_id);
CREATE INDEX IF NOT EXISTS idx_mem_user ON agent_memories(user_id);
CREATE INDEX IF NOT EXISTS idx_llm_task ON llm_requests(task);
