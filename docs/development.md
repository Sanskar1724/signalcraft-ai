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
