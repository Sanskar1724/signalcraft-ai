# SignalCraft AI — Prompt-Aligned Implementation Plan

Source of truth: `prompt.txt` (36 sections). This doc maps each section to concrete modules.
Stack decision (§3, §6): modular monolith, Streamlit + SQLite + stdlib-first, offline-capable.

## Core loop (§2, §28 MVP)
```
Creator -> Profile -> Research -> Trends -> Opportunities -> Strategy
  -> Content Agent -> LinkedIn/X/Blog -> Library -> Performance
  -> Analytics -> Insights -> Memory -> Next Decision
```

## Module map
| Prompt | Requirement | Implementation |
|---|---|---|
| §1 Product | personal strategist, not generic writer | `profiles.py` drives research/rank/generate; `agent.py` orchestrates |
| §5 Model strategy | best tool per job, abstraction | `llm/providers.py` (Mock + OpenAI-compatible), `llm/gateway.py` (`generate`, `structured_generate`, `embed`, task routing, `llm_requests` tracking) |
| §6 No over-engineering | modular monolith | single Streamlit app, SQLite, no microservices |
| §7 User intelligence | profile influences all | `profiles.py` (12 fields), keywords() used by trends/opps/generator |
| §8 Current info | pluggable sources, no fabrication | `research/base.py` interface; `rss.py` live; `samples.py` labeled `sample://`; stubs: `github.py`, `reddit.py`, `youtube.py`; `manager.py` dedupes + preserves `source_url` |
| §9 Content intelligence | personalized ranking, transparent | `trends.py`: `score = 100*(0.20*fresh + 0.15*growth + 0.20*rel + 0.15*aud_fit + 0.10*nov + 0.05*(1-comp) + 0.15*creator_fit)` documented in code + docs |
| §10 Opportunity | 11 fields + why-explanation | `opportunities.py`, table `opportunities`, UI shows why_now / why_you / evidence |
| §11 Content agent | 13-stage controlled workflow, bounded, observable | `agent.py`: intent -> profile -> memory -> research -> trend -> opp -> strategy -> generate -> critique -> store; `Trace` from `observability.py`; max 2 revise loops, max 8 tool calls, timeout guard |
| §12 Multi-platform | LinkedIn/X/Blog transforms | `content/platforms.py` (real transforms), `generator.py` entry point, easy to add `instagram.py` later |
| §13 Quality | rubric + bounded Generate->Critique->Improve | `content/critic.py` (10 checks -> 0-10), `generator.py` revises once if <7.5 |
| §14 Memory | structured + semantic-ready, selective | `memory.py` (`successful_topic`, `weak_topic`, `preferred_format`, `insight`); `embed()` ready for vector later; `learn_from_performance()` |
| §15 Analytics | manual entry MVP, best/worst | `analytics.py` (`record_performance`, `summary`, `insights`); UI manual form + charts |
| §16 Learning loop | structured insights adjust recs | `get_memory_boost()` in [-8,+8] applied in `opportunities.py` |
| §17 Dashboard | 10 sections, decisions over decoration | `app.py` pages: Overview, Trending For You, Opportunities, Create, Library, Analytics, Calendar, Insights, Agent, Settings |
| §18 Agent chat | tool-using answers, no hallucinated data | `agent.py` answers with DB tools; data questions always query DB first |
| §19 LLM arch | generate/structured/embed + metadata | done in gateway; `TASK_MODEL_HINTS` routing |
| §20 Data arch | relational source of truth | `db.py` 12 tables: users, profiles, research_items, trends, opportunities, content_items, content_versions, performance, memories, llm_requests, calendar_entries (+ recommendations view via opportunities) |
| §21 Background | async-ready, simple MVP | `research/manager.py` + Streamlit `@st.cache_data(ttl=900)` + "Refresh research" job; documented Celery/GH-Actions path |
| §22 API design | clean validated APIs | each module exposes typed functions with validation; `docs/api.md` |
| §23 Security | auth, secrets, validation | `.env.example`, no secrets in code, input length caps, single-user local MVP with `users` table ready for Auth0/Supabase later |
| §24 Observability | full trace visible | `Trace` rendered in Agent page expander + logs |
| §25 Testing | business/API/agent/frontend | `tests/` with mocked LLM (MockProvider), no live calls |
| §30 UI quality | professional intelligence dashboard | light theme, cards, empty/loading/error states, responsive columns |
| §31 Grounding | sources preserved; fact vs interpretation vs recommendation | research cards always show source+URL; opportunity page has 3 labeled blocks: Observed fact / Interpretation / Recommendation |
| §32 Cost/perf | cache, retrieval, summaries, small models | cache research/trends 15 min, bounded context (top 5 evidence, 220-char prompts), Mock/fast tasks local |
| §33 GitHub quality | portfolio-ready docs | README, docs/architecture.md, docs/api.md, docs/roadmap.md, setup + testing instructions |

## Build order (§26)
Foundation(done) -> DB(done) -> Profiles(done) -> Research(done, +stubs) -> Trends(done)
  -> Opportunities(done) -> LLM gateway(done) -> Critic -> Generator -> Memory(done)
  -> Analytics -> Dashboard -> Agent -> Testing -> Docs -> Push.

## MVP acceptance (§28)
One click demonstrates: seeded profile -> refresh research (sample+RSS) -> trends scored
-> opportunities with why -> generate LinkedIn/X/Blog -> critique score -> save library
-> enter performance -> analytics + insight -> memory boost changes next ranking.
