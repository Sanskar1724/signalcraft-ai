"use client";

import { useState } from "react";
import { api } from "../../../lib/api";
import { Card, Empty, Loading, ScoreBar, Tabs, useApi } from "../../../components/ui";

export default function TrendingPage() {
  const { data, error, busy } = useApi(() => api.trends());
  const [query, setQuery] = useState("");
  const [sort, setSort] = useState("trend_score");

  if (busy) return (<><h1>Trending For You</h1><Loading /></>);
  if (error || !data) return (<><h1>Trending For You</h1><div className="error">API unavailable: {error}</div></>);

  const rows = data
    .filter((t) => !query || t.topic.toLowerCase().includes(query.toLowerCase()))
    .sort((a, b) => (b[sort as keyof typeof b] as number) - (a[sort as keyof typeof a] as number));

  return (
    <>
      <h1>Trending — filtered for you</h1>
      <p className="sub">
        Trend score = 30% growth + 25% freshness + 20% relevance + 15% source momentum +
        10% novelty. Weights configurable — never a black box.
      </p>
      <div className="row">
        <div style={{ flex: 2, minWidth: 200 }}>
          <input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Filter topics…" />
        </div>
        <Tabs tabs={["trend_score", "freshness", "growth", "relevance"]} active={sort} onChange={setSort} />
      </div>
      {rows.length === 0 && <Empty text="No topics match — clear the filter." />}
      {rows.map((t) => (
        <Card key={t.topic}>
          <h3>{t.topic} — {t.trend_score}</h3>
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
        </Card>
      ))}
    </>
  );
}
