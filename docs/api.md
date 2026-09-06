# API

All calls are typed Python functions (no separate HTTP server in MVP, §22).

- Profiles: `get_profile()`, `update_profile()`, `seed_default_profile()`
- Research: `collect_and_store(query, limit, use_live)`, `list_recent()`, `search()`
- Trends: `detect_trends(top_n)` -> `[{topic, freshness, growth, relevance, novelty, score, evidence}]`
- Opportunities: `build_opportunities()`, `list_opportunities()`
- Content: `generate_content(opportunity_id, platform)`, `list_content()`, `critique(body, platform, topic)`
- Analytics: `record_performance(...)`, `summary()`, `insights()`
- Memory: `remember()`, `recall()`, `get_memory_boost()`, `learn_from_performance()`
- Agent: `run(request)` -> `{answer, intent, trace[, content_id]}`
- Calendar: `schedule()`, `upcoming()`
- LLM: `LLMGateway().generate / structured_generate / embed`

Validation: profile fields allow-listed; performance metrics must be >= 0;
`generate_content` raises `ValueError` on unknown opportunity; bodies capped at 6000 chars.
