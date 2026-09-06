# Architecture

Modular monolith: Streamlit (`app.py`) + SQLite (`src/signalcraft/db.py`) + deterministic engines.
LLM is a tool behind `LLMGateway`, never the database.

```
app.py (10 pages)
  -> profiles / research / trends / opportunities
  -> content/{generator, platforms, critic} / analytics / memory
  -> agent (controlled workflow) + observability.Trace
  -> llm/{gateway, providers} (Mock offline, OpenAI-compatible optional)
```

## Key decisions
- SQLite WAL, 12 tables, `source_url` preserved on every research row (§31 grounding).
- Trend score is a documented weighted sum; memory applies a bounded [-8,+8] boost.
- Content revise loop runs at most once; agent makes at most ~8 tool calls.
- New research sources implement `fetch()` — no core rewrite (§8).
- New platforms add one formatter in `content/platforms.py` (§12).

## Data tables
users, profiles, research_items, trends, opportunities, content_items,
content_versions, performance, memories, llm_requests, calendar_entries.
