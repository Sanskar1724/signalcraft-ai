# SignalCraft AI — Your personal AI content strategist

SignalCraft AI understands **you** (profile), **what is happening now** (research),
**what matters to you** (trend intelligence), tells you **what to post**
(opportunities with why-explanations), helps you **say it per platform**
(LinkedIn / X / Blog + critique loop), and **learns from performance** (analytics → memory).

## Quickstart
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate  |  macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
copy .env.example .env   # optional; app works offline without keys
pytest -q
streamlit run app.py
```

## Example workflow
1. Sidebar → **Seed demo profile** (AI + Data Engineering creator).
2. **Refresh research + trends** (RSS live with offline sample fallback).
3. **Trending For You** → transparent scores + evidence.
4. **Opportunities** → Observed fact / Interpretation / Recommendation per card.
5. **Create** → generate LinkedIn/X/Blog draft with quality score.
6. **Analytics** → manually log impressions/likes/comments → charts.
7. **Insights** → creator insights + **Learn from performance → memory**.
8. **Agent** → ask "What should I post today?" with execution trace.

## Architecture
Modular monolith: `app.py` + `src/signalcraft/` + SQLite (`data/signalcraft.db`).
See `docs/IMPLEMENTATION_PLAN.md`, `docs/architecture.md`, `docs/api.md`, `docs/roadmap.md`.

## Trend formula
`score = 100 × (0.30·freshness + 0.25·growth + 0.25·relevance + 0.20·novelty)`,
plus a bounded memory boost in [-8, +8]. No black boxes.

## Grounding
Research rows preserve `source` + `source_url`. Sample rows are labeled `sample://`
and shown as samples — never presented as live news. UI separates
Observed fact / AI interpretation / AI recommendation.

## Testing
`pytest -q` — offline, LLM mocked (`MockProvider`), no live calls.
