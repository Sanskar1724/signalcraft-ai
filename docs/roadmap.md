# Roadmap

Next, in order:
1. Real source wiring (GitHub/Reddit/YouTube API keys, `research/extra_sources.py`).
2. Scheduled refresh (GitHub Action / cron hitting `collect_and_store` + `build_opportunities`).
3. Supabase/Auth + hosted Postgres (schema ports 1:1 from SQLite).
4. Publishing adapters (LinkedIn/X APIs) behind the platform interface.
5. A/B experiments + performance prediction from `performance` history.
6. Team workspaces + billing.
