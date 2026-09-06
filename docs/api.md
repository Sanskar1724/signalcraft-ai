# API (§23)

Base: `/api` (prefix constant, versionable to `/api/v1`). Errors use
`{"error": {"code", "message", "request_id"}}`; every response carries
`X-Request-ID`. Auth: `X-API-Key` when `SIGNALCRAFT_API_KEY` is set, else open
local mode (§24).

| Method & path | Purpose |
|---|---|
| GET `/api/health` | liveness |
| POST `/api/auth/signup` · POST `/api/auth/login` | session auth (public) |
| POST `/api/auth/logout` · POST `/api/auth/password` | session end / rotation |
| GET `/api/auth/me` | user + onboarding status (routing) |
| GET `/api/onboarding/status` · POST `/api/onboarding` | stepwise persisted setup |
| POST `/api/onboarding/complete` | validate + build intelligence + COMPLETED |
| GET `/api/profile` · PUT `/api/profile` | creator profile (§7, §14) |
| GET `/api/preferences` · PUT `/api/preferences` | content + AI controls (§15) |
| GET `/api/context` | Creator Context for debugging (§13) |
| GET `/api/trends?top_n=` | trend signals (§10) |
| GET `/api/opportunities?refresh=` | ranked opportunities (§11) |
| POST `/api/research` `{query, limit, use_live}` | refresh pipeline (§8-§9) |
| POST `/api/content/generate` | brief → draft → critique → store |
| POST `/api/content/critique` | structured rubric score (§15) |
| POST `/api/content/revise` | bounded improvement pass, new version |
| GET `/api/content` · GET `/api/content/{id}` | library + detail (§19) |
| POST `/api/content/{id}/performance` | manual metric entry (§17) |
| GET `/api/analytics` · GET `/api/insights` | scores + creator insights |
| POST `/api/agent/chat` | orchestrator answer + trace (§20) |
| GET `/api/agent/memory` | durable memories (§16) |
| GET/POST `/api/calendar` | planned content (§19) |
| GET `/api/debug/llm` | provider/model/task/latency/cost stats (§25) |

Pagination: `limit`/`offset` on list routes. Run the API:
`uvicorn apps.api.app.main:app --app-dir . --reload`. Tests:
`pytest apps/api/tests -q` (TestClient, no network).
