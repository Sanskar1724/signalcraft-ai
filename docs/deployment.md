# Deployment guide

## What to collect before deploying

| # | Item | Where it goes | Required? |
|---|---|---|---|
| 1 | Backend public URL (e.g. `https://signalcraft-api.up.railway.app`) | Vercel env `NEXT_PUBLIC_API_URL` | yes |
| 2 | `SIGNALCRAFT_API_KEY` — generate one (`python -c "import secrets; print(secrets.token_hex(32))"`) | backend env + Vercel only if the web app proxies (it doesn't — browser calls the API directly, so the key would be public; see note below) | only for non-browser clients |
| 3 | `OPENROUTER_API_KEY` | backend env | no — Mock provider works offline |
| 4 | `CHEAP_MODEL` / `STRONG_MODEL` | backend env | no (defaults are Mock) |
| 5 | Python version for the host | `3.12` (matches `apps/api/Dockerfile`) | yes |
| 6 | Backend start command | `uvicorn apps.api.app.main:app --app-dir . --host 0.0.0.0 --port $PORT` (see `Procfile`) | yes |
| 7 | SQLite persistence decision | volume mount, or accept ephemeral data | yes — read below |

Auth note: the Next.js app calls the API from the browser, so an `X-API-Key`
sent by the frontend is visible to users. For a personal deployment, leave
`SIGNALCRAFT_API_KEY` **unset** (open mode) or put the API behind the host's
private networking. Turn auth on when you add server-side callers.

SQLite note: hosts with ephemeral filesystems wipe `data/signalcraft.db` on
redeploy/restart. For a personal demo that is acceptable (re-run
`scripts/seed.py`); for anything durable, attach a **volume** (Railway/Render/
Fly all support this) and set `SIGNALCRAFT_DB_PATH` to it. The Postgres +
pgvector cutover is designed in `docs/database.md`.

## Frontend — Vercel (recommended)

1. Push this repo to GitHub (done).
2. Vercel → Add New Project → import `signalcraft-ai`.
3. **Root Directory:** `apps/web` (the repo root has no `package.json`).
4. Framework preset: Next.js (auto-detected). Build: `npm run build`.
5. Environment variable: `NEXT_PUBLIC_API_URL` = your backend public URL.
6. Deploy. Verify: Overview, Opportunities and Agent pages load data.
7. Backend CORS: after Vercel gives you the frontend URL, add it to the
   backend's `CORS_ORIGINS` (comma-separated, e.g.
   `CORS_ORIGINS=http://localhost:3000,https://signalcraft-web.vercel.app`)
   and redeploy the API — otherwise browsers block the dashboard's requests.

## Backend — recommended hosts

**Vercel is not recommended for this API.** Serverless functions have a
read-only filesystem (SQLite can't persist), cold starts, and execution
timeouts — a bad fit for a stateful FastAPI + SQLite service.

| Host | Why | Notes |
|---|---|---|
| **Railway (recommended)** | Nixpacks auto-builds from root `requirements.txt`; volumes for SQLite; `$PORT` provided | Set start command to the `Procfile` command; attach a volume at `/data`, set `SIGNALCRAFT_DB_PATH=/data/signalcraft.db` |
| **Render** | Simple web services + persistent disks | Same start command; add a disk mounted at `/data` |
| **Fly.io** | Volumes, generous free allowance, Docker-native | `fly launch` from `apps/api/Dockerfile`; attach a volume |

All three can also run `docker compose` equivalents; the provided
`docker-compose.yml` is for VPS/single-host deploys (needs a Docker daemon,
which this dev machine doesn't have — compose is untested here).

## Post-deploy verification checklist

```bash
BASE=https://<your-backend>
curl $BASE/api/health
curl "$BASE/api/trends?top_n=3"
curl "$BASE/api/opportunities?limit=3"
```

Then in the dashboard: Overview shows recommendations → Create generates a
LinkedIn draft → Analytics logs a metric → Agent answers "What should I post
today?" with data. If research looks empty, POST `/api/research` once.
