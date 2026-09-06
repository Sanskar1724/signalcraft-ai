# SignalCraft AI — Your personal AI content strategist

SignalCraft AI understands **you** (profile), **what is happening now** (research),
**what matters to you** (trend intelligence), tells you **what to post**
(opportunities with why-explanations), helps you **say it per platform**
(LinkedIn / X / Blog + brief → draft → critique loop), and **learns from
performance** (analytics → memory → better recommendations).

Spec: `prompt1.txt` (40 sections). Plan: `docs/IMPLEMENTATION_PLAN.md`.

## Architecture

Modular monolith (§4):

```
apps/web (Next.js 14 + TypeScript)  ── fetches ──▶  FastAPI (/api/*)
apps/api (routers → services → agents/providers/analytics)
                        │
                        ▼
src/signalcraft (domain modules: profiles, research, trends,
  opportunities, content, memory, analytics, agent, llm, jobs)
                        │
                        ▼
SQLite (`data/signalcraft.db`, §6 entities, UUIDs, indexes, migrations)
```

Providers (LLM, web search, RSS, …) sit behind interfaces; app code uses the
`LLMGateway` (`generate` / `structured_generate` / `embed`).

## Setup

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate | macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # optional; offline defaults work without keys
python scripts/seed.py --fresh   # demo creator + 21 content items + performance
```

## Running locally

```bash
make test                         # pytest: domain + API (offline, mocked LLM)
uvicorn apps.api.app.main:app --app-dir . --reload --port 8000   # REST API
cd apps/web && npm install && npm run dev                        # dashboard :3000
streamlit run app.py              # legacy local dashboard (deprecated, use web)
```

Docker (daemon not verified in this environment — files provided per spec):

```bash
docker compose up --build   # web :3000, api :8000 (+ postgres/redis reserved)
```

## Environment variables

See `.env.example`. Keys: `SIGNALCRAFT_API_KEY` (API auth; unset = open local
mode), `OPENROUTER_API_KEY` (initial live LLM; unset = Mock offline),
`CHEAP_MODEL` / `STRONG_MODEL` (task routing), `QUALITY_THRESHOLD` /
`MAX_RETRIES` (critic loop), `TREND_WEIGHTS_JSON` / `OPP_WEIGHTS_JSON`
(scoring weights), `NEXT_PUBLIC_API_URL`.

## Database setup

SQLite by default; `signalcraft.db.init_db()` creates the §6 schema and runs
additive migrations (legacy renames, UUID backfill). SQL versions live in
`apps/api/migrations/`. Postgres + pgvector + Redis are composed for the
cutover — see `docs/database.md`.

## Testing

`pytest -q` — 27 tests: trend/opportunity scoring, analytics, platform
formatting, validation, research pipeline, LLM gateway (mocked, no live
calls), REST API incl. auth, agent tool selection/retry limits. Frontend:
`npm run typecheck` + `npm run build` in `apps/web`.

## Agent workflow

`docs/agent.md`. One orchestrator, 9 named tools, bounded (8 calls, 60s),
content brief before every draft, Pydantic-validated structured outputs,
full execution trace per request.

## LLM configuration

`OPENROUTER_API_KEY` → OpenRouter provider; else Mock (deterministic,
offline). Cheap tasks (classification, extraction, tagging, summarization)
route to `CHEAP_MODEL`; strategy/generation/critique to `STRONG_MODEL`.
Every call is logged with provider/model/task/latency/tokens/cost
(`GET /api/debug/llm`).

## Research configuration

RSS live + labeled offline samples by default; GitHub/Reddit/YouTube/News/web
search/trends are pluggable sources (`research/extra_sources.py`) returning
empty until keys are wired — the pipeline continues with available sources
and marks limitations (§32).

## Known limitations

- Single-user local mode (multi-user/auth provider is future work).
- SQLite + local hash embeddings (Postgres/pgvector cutover designed, not cut).
- No social publishing, billing, teams (see MVP boundary, §29).

## Future roadmap

`docs/roadmap.md`: publishing adapters, scheduling, competitor analysis,
A/B testing, performance prediction, more LLM providers.
