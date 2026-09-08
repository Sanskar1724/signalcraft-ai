"use client";

import { useState } from "react";
import { api, type TrendSignal } from "../../../lib/api";
import { TrendDrawer, direction } from "../../../components/Drawers";
import { Card, Empty, Loading, ScoreBar, Tabs, useApi } from "../../../components/ui";

export default function TrendingPage() {
  const [tab, setTab] = useState("for_you");
  const [query, setQuery] = useState("");
  const [sel, setSel] = useState<TrendSignal | null>(null);
  const { data, error, busy, reload } = useApi(() => api.trends(12, tab), [tab]);
  const opps = useApi(() => api.opportunities());

  if (busy) return (<><h1>Trending For You</h1><Loading /></>);
  if (error || !data) return (<><h1>Trends</h1><div className="error">We couldn&apos;t load today&apos;s trends.
    <p><button className="btn small" onClick={reload}>Retry</button></p></div></>);

  const rows = (data ?? [])
    .filter((t) => !query || t.topic.toLowerCase().includes(query.toLowerCase()));

  return (
    <>
      <h1>Trends</h1>
      <p className="sub">
        Scored for your niche — switch views to slice by momentum or recency.
      </p>
      <Tabs tabs={["for_you", "rising", "latest"]} active={tab} onChange={setTab} />
      <div className="row" style={{ marginTop: 10 }}>
        <div style={{ flex: 2, minWidth: 200 }}>
          <input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Filter topics…" aria-label="Filter topics" />
        </div>
      </div>
      <p className="sub muted">Weights: 30% growth · 25% freshness · 20% relevance · 15% momentum · 10% novelty.</p>
      {rows.length === 0 && <Empty text="No topics match — clear the filter." />}
      {rows.map((t) => (
        <Card key={t.topic} lift>
          <div style={{ cursor: "pointer" }} onClick={() => setSel(t)}>
            <h3>{t.topic} — {t.trend_score} <span className="muted">· {direction(t.growth)}</span></h3>
            <ScoreBar value={t.trend_score} />
          <div className="dims">
            <span>Growth {t.growth}</span>
            <span>Freshness {t.freshness}</span>
            <span>Relevance {t.relevance}</span>
            <span>Momentum {t.source_momentum}</span>
            <span>Novelty {t.novelty}</span>
            <span>Audience {t.audience_fit}</span>
            <span>Competition {t.competition}</span>
          </div>
          {(t.evidence_titles ?? []).length > 0 && (
            <details className="trace" onClick={(e) => e.stopPropagation()}>
              <summary>Evidence ({t.evidence_titles!.length} sources)</summary>
              {(t.evidence_titles ?? []).map((e, i) => (
                <p key={i} className="muted">· {e}</p>
              ))}
            </details>
          )}
          </div>
        </Card>
      ))}
      {sel && <TrendDrawer trend={sel} opportunities={opps.data ?? []}
        onClose={() => setSel(null)} onChanged={() => { reload(); opps.reload(); }} />}
    </>
  );
}
