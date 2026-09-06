# SignalCraft AI — prompt1.txt Implementation Plan (§40)

Constitution: `prompt1.txt` (40 sections). Phase order per §28.

| Phase | Spec | Implementation | Status |
|---|---|---|---|
| 1 foundation | §3-§5 | monorepo `apps/{api,web}`, `packages/shared`, `scripts/`, `Makefile`, `.env.example` | done |
| 2 database | §6 | §6 names, UUIDs, timestamps, indexes, `_migrate()` + `migrations/*.sql` | done |
| 3 auth+profile | §7, §24 | 14-field profile, taxonomy sync, API-key auth (open local mode) | done |
| 4 research | §8-§9 | RSS live + 6 pluggable stubs, normalize/dedupe/enrich/store | done |
| 5 trends | §10 | 7 signals, Trend Score = 30/25/20/15/10 (§10 example), configurable weights | done |
| 6 opportunities | §11 | separate Opportunity Score (§11 weights), why-explanations, recommendations log | done |
| 7 LLM gateway | §21, §34 | Mock/OpenRouter/OpenAI-compat, cheap-vs-strong routing, cost tracking | done |
| 8 generation | §13-§14 | validated `ContentBrief` → draft; platform `rules.py` config | done |
| 9 critic | §15, §32 | 10-check rubric, `QUALITY_THRESHOLD`/`MAX_RETRIES`, fallback never crashes | done |
| 10 memory | §16 | 8 kinds, feedback, semantic recall (pgvector-ready) | done |
| 11 analytics | §17-§18 | manual entry, Content Performance Score, deterministic insights → memory | done |
| 12 dashboard | §19, §31 | Next.js 9 pages + typed client | done |
| 13 agent chat | §12, §20 | orchestrator, 9 named tools, budgets, traces, request IDs | done |
| 14 testing | §26 | 27 pytest (unit/integration/API/agent) + `tsc` + `next build` | done |
| 15 docker | §3, §39 | Dockerfiles + compose (daemon not verifiable here — noted) | done |

MVP boundary (§29): all 14 bullets supported; publishing/billing/teams/mobile/
fine-tuning excluded by design. DoD (§39): 22-item loop verified — profile →
research → trends → opportunities → dashboard → brief → LinkedIn/X/Blog →
critic → revise → store → history → performance → analytics → insights →
memory → better ranking → agent chat on real data → tests pass → README complete.
