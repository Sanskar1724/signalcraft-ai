# SignalCraft AI

**Your personal AI content strategist** — not another AI writing tool.

SignalCraft AI learns who a creator is, watches what is happening in their
niche right now, and tells them *what to talk about, how to say it on each
platform, and what to do next* based on what actually performed.

Built to a written product specification (`prompt1.txt`): profile → research →
trend intelligence → personalized opportunities → content agent → LinkedIn / X /
Blog drafts → critique → performance analytics → memory → better recommendations.

## Features

- **Creator profile** — niche, expertise, audience, goals, platforms, style, tone,
  topics, avoid-list, content and posting preferences drive everything.
- **Research engine** — RSS live collection plus clearly-labeled offline samples;
  GitHub, Reddit, YouTube, News, web search and search-trends plug in behind one
  interface. Sources and URLs are always preserved.
- **Trend intelligence** — transparent Trend Score (30% growth, 25% freshness,
  20% relevance, 15% source momentum, 10% novelty; weights configurable).
- **Content opportunities** — a separate Opportunity Score with trend, relevance,
  audience fit, freshness and competition, each explained (observed fact →
  interpretation → recommendation).
- **Content agent** — one orchestrator, nine named tools, bounded execution.
  Every draft is generated from a validated structured brief with supporting
  evidence, then critiqued (10 checks) and revised within strict retry limits.
- **Multi-platform output** — LinkedIn, X threads and Blog posts, each rendered
  from platform rules (never truncated copies).
- **Analytics & learning loop** — manual metric entry, engagement rate, Content
  Performance Score, best/worst topics, formats and hooks; insights feed creator
  memory and re-rank future recommendations.
- **Agent chat** — answers from real application data with full execution traces.
- **LLM gateway** — Mock (offline) / OpenRouter / OpenAI-compatible providers,
  cheap-vs-strong task routing, per-call latency/token/cost tracking.

## Tech stack

| Layer | Technology |
|---|---|
| Frontend | Next.js 14, TypeScript, CSS |
| Backend | Python, FastAPI, Pydantic |
| Domain core | Typed Python modules (`src/signalcraft`) |
| Database | SQLite (Postgres + pgvector path designed) |
| LLM | OpenRouter gateway with offline Mock fallback |
| Infra | Docker, docker-compose, Makefile |

## Quickstart

Prerequisites: Python 3.12+, Node 20+.

```bash
git clone https://github.com/Sanskar1724/signalcraft-ai.git
cd signalcraft-ai
python -m venv .venv
# Windows: .venv\Scripts\activate | macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # optional — offline defaults work with no keys
python scripts/seed.py --fresh  # demo creator, 21 drafts, performance history
```

Run the backend and frontend in two terminals:

```bash
# Terminal 1 — REST API on :8000
uvicorn apps.api.app.main:app --app-dir . --reload

# Terminal 2 — dashboard on :3000
cd apps/web && npm install && npm run dev
```

Open http://localhost:3000. The API docs live at http://localhost:8000/docs.

## Configuration

All settings are environment-first; see `.env.example` for the full list.

| Variable | Purpose | Default |
|---|---|---|
| `SIGNALCRAFT_API_KEY` | API auth (`X-API-Key`); unset = open local mode | — |
| `OPENROUTER_API_KEY` | Live LLM provider; unset = offline Mock | — |
| `CHEAP_MODEL` / `STRONG_MODEL` | Task-based model routing | `mock` |
| `QUALITY_THRESHOLD` / `MAX_RETRIES` | Critic revise loop bounds | `7.5` / `1` |
| `TREND_WEIGHTS_JSON` / `OPP_WEIGHTS_JSON` | Scoring weight overrides | spec defaults |
| `NEXT_PUBLIC_API_URL` | Backend URL for the web app | `http://localhost:8000` |

## API reference

Full table in [`docs/api.md`](docs/api.md). Highlights:

```
GET    /api/health                        GET    /api/trends
GET    /api/profile       PUT /api/profile  GET    /api/opportunities
POST   /api/research                      POST   /api/content/generate
POST   /api/content/critique              POST   /api/content/revise
GET    /api/content       GET /api/content/{id}
POST   /api/content/{id}/performance      GET    /api/analytics
GET    /api/insights                      POST   /api/agent/chat
```

## Testing

```bash
pytest -q            # 22 tests: scoring, analytics, pipeline, gateway, REST + auth, agent
cd apps/web && npm run typecheck && npm run build
```

LLM calls are mocked — the suite needs no network and no API keys.

## Project structure

```
apps/api/        FastAPI service (routers → services → agents/providers)
apps/api/migrations/  SQL migration history
apps/web/        Next.js dashboard (9 pages + typed API client)
packages/shared/ Shared API contracts
src/signalcraft/ Domain core (profiles, research, trends, opportunities,
                 content, memory, analytics, agent, llm, jobs, security)
scripts/         seed.py — realistic, clearly-marked demo data
docs/            architecture, api, database, agent, development,
                 deployment, roadmap, implementation plan
prompt1.txt      Product specification this repo implements
```

## Deployment

See [`docs/deployment.md`](docs/deployment.md) for the pre-deploy checklist,
environment variables to collect, and platform recommendations (Vercel for the
frontend; Railway/Render/Fly.io for the API).

## Roadmap

Publishing adapters, automatic scheduling, competitor analysis, A/B testing,
performance prediction, more LLM providers — details in
[`docs/roadmap.md`](docs/roadmap.md).
