# Agent (§11, §18, §24)

Controlled workflow in `src/signalcraft/agent.py`, max 8 tool calls, 60s budget.

```
request -> validate + rate limit -> intent -> profile -> memory
  -> analyze: analytics.summary + insights
  -> transform_*: top opportunity + generate_content(platform)
  -> trends/ideas/recommend/why/angle/general: research.search + opportunities.list
  -> answer in three blocks: Observed fact / Interpretation / Recommendation
```

Intents: `analyze`, `transform_linkedin`, `transform_x`, `transform_blog`,
`trends`, `ideas`, `recommend`, `why`, `angle`, `general`.
Every run returns `{answer, intent, trace[, content_id]}`; the trace is
rendered in the Agent page expander. Data questions always query the DB —
never model knowledge alone (§18).
