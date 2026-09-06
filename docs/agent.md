# Agent (§12, §20, §25, §35)

ONE orchestrator (`src/signalcraft/agent.py`), tools in
`apps/api/app/agents/tools.py`. Bounded: 8 tool calls, 60s budget, 1 revise
loop, validated inputs/outputs. No unlimited autonomy.

```
request → validate + rate limit → intent → profile → memory → research?
→ trends → history/performance → opportunity → brief (§13) → generate
→ critique (§15) → improve? → validate → store → answer
```

Named tools: `get_user_profile`, `get_user_memory`, `search_research`,
`get_trending_topics`, `get_content_history`, `get_content_performance`,
`rank_opportunities`, `generate_content`, `critique_content` — each with a
`TOOL_SCHEMAS` budget. Tools answer from the DB, never from model knowledge
alone (§20). Every run returns `{answer, intent, trace, request_id}` in three
blocks: Observed fact / Interpretation / Recommendation (§33). Debug:
`GET /api/debug/llm` + per-request traces in the Agent UI.
