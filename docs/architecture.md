# Architecture (§4-§5)

Modular monolith. No microservices.

```
apps/web/app/*          Next.js 14 pages (Overview, Trending, Opportunities,
                        Create, Library, Analytics, Calendar, Insights, Agent)
apps/web/lib/api.ts     Typed client for every REST route
        │ fetch (NEXT_PUBLIC_API_URL, no secrets in frontend)
        ▼
apps/api/app/main.py    FastAPI (routers → services → agents/providers/analytics)
apps/api/app/api/       deps (API-key auth), router (§23 routes), error envelope
apps/api/app/schemas/   Request bodies (Pydantic, validated at boundary)
apps/api/app/models/    Read models mirroring §6 entities
apps/api/app/services/  Use cases calling domain modules (no logic duplication)
apps/api/app/repositories/  Detail queries (content + versions + performance)
apps/api/app/providers/ LLM registry (mock/openrouter/openai_compatible)
apps/api/app/agents/    9 named tools (§12) + per-tool budgets (§35)
apps/api/app/analytics/ Passthrough (calculations live in domain)
        │
        ▼
src/signalcraft/        Domain modules (UI-independent, fully tested)
  profiles · taxonomy · research/{rss,extra_sources,manager} · trends
  opportunities · content/{generator,platforms,rules,critic} · memory
  analytics · agent · calendar · jobs · security · llm/{gateway,providers,
  prompts,schemas} · observability · db · config
        │
        ▼
SQLite (§6 entities, UUIDs, timestamps, indexes; migrations in db._migrate
+ apps/api/migrations/*.sql). Postgres/pgvector + Redis composed for cutover.
        │
        ▼
External providers      LLM (OpenRouter→OpenAI-compat→Mock fallback chain)
                        Web search / RSS / (GitHub, Reddit, YouTube, News…)
```

## Key decisions
- Domain owns logic; API/web are thin (reuse per §38, no duplicate utilities).
- Trend Score (§10, configurable) and Opportunity Score (§11) are separate,
  documented formulas — never black boxes.
- Every draft is built from a validated `ContentBrief` (§13) + evidence
  titles (§33); platform output follows `content/rules.py` config (§14).
- Bounded agent: 8 tool calls, 60s budget, 1 revise loop (§35).
- `streamlit app.py` remains as a local dashboard but is deprecated in favor
  of `apps/web`.
