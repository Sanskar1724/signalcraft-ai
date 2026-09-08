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
| PUT `/api/opportunities/{id}/dismiss` | dismiss + weak-topic memory |
| POST `/api/research` `{query, limit, use_live}` | refresh pipeline (§8-§9) |
| GET `/api/research?q=` | normalized research documents |
| POST `/api/content/generate` | brief → draft → critique → validate → **preview** (nothing stored) |
| POST `/api/content/save` | explicit Save → library record + v1 |
| POST `/api/content/critique` | structured rubric score (§15) |
| POST `/api/content/improve-preview` | improve a preview without storing |
| POST `/api/content/revise` | improve stored content → version+1 |
| DELETE `/api/content/{id}` | delete (+ cascade versions/performance) |
| POST `/api/content/{id}/duplicate` | copy as fresh draft with history |
| PUT `/api/content/{id}/status` | move draft/ready/published/archived |
| GET `/api/content` · GET `/api/content/{id}` | library + detail (§19) |
| POST `/api/content/{id}/performance` | manual metric entry (§17) |
| GET `/api/analytics` · GET `/api/insights` | scores + creator insights |
| POST `/api/agent/chat` | orchestrator answer + trace + actions (§20) |
| GET `/api/agent/memory` · POST `/api/agent/memory` | durable memories (§16) |
| GET/POST `/api/calendar` | planned content (§19) |
| PUT `/api/calendar/{id}` | reschedule / edit / mark published |
| POST `/api/calendar/{id}/duplicate` | copy as draft |
| GET `/api/auth/google/status` | OAuth configuration state (never faked) |
| GET `/api/debug/llm` | provider/model/task/latency/cost stats (§25) |

Pagination: `limit`/`offset` on list routes. Run the API:
`uvicorn apps.api.app.main:app --app-dir . --reload`. Tests:
`pytest apps/api/tests -q` (TestClient, no network).
