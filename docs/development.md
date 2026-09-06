# Development guide

```bash
make setup && cp -n .env.example .env
make test            # pytest: domain (tests/) + API (apps/api/tests)
make seed            # demo data
make api             # uvicorn :8001
make web             # next dev :3001 (cd apps/web, npm install first)
make docker-up       # full stack (needs Docker daemon)
```

Conventions (§38): reuse domain logic (no duplicate utilities), small
modules, business logic out of UI, providers behind interfaces, DB logic in
`db.py`/repositories, validate external input (API schemas, `security`) and
LLM output (`llm/schemas.py`), tests for scoring/ranking/analytics/agent,
docs updated with architecture changes. Commits: `feat:`/`test:`/`chore:`.
`prompt1.txt` is the constitution; keep a working system at every phase (§40).

## Google OAuth setup

1. Google Cloud Console → new project → **OAuth consent screen** (External):
   app name `SignalCraft AI`, support email yours, scopes stay
   `openid email profile`, add your Gmail under **Test users**.
2. **Credentials → Create Credentials → OAuth client ID** (Web application).
3. Authorized redirect URIs (exact, no trailing slash):
   - local: `http://localhost:8001/api/auth/google/callback`
   - prod: `https://<your-api>/api/auth/google/callback`
4. Put the ID + secret in backend `.env` as `GOOGLE_CLIENT_ID` /
   `GOOGLE_CLIENT_SECRET` (never in frontend code) and restart the API.
5. Flow: button → `GET /api/auth/google/start` (302, one-time CSRF state) →
   Google → `GET /api/auth/google/callback` (validates state, verifies
   email, find-or-creates the user, mints a session) → frontend
   `/auth/callback?token=…` → dashboard/onboarding by status.
   Without credentials the button reports setup state and never fakes a login.
