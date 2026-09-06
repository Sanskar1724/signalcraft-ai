"use client";

import { api } from "../../lib/api";
import { Card, Empty, Loading, ScoreBar, useApi } from "../../components/ui";

export default function TrendingPage() {
  const { data, error, busy } = useApi(() => api.trends());

  if (busy) return (<><h1>Trending For You</h1><Loading /></>);
  if (error || !data) return (<><h1>Trending For You</h1><div className="error">API unavailable: {error}</div></>);

  return (
    <>
      <h1>Trending — filtered for you</h1>
      <p className="sub">
        Trend score = 30% growth + 25% freshness + 20% relevance + 15% source momentum +
        10% novelty. Weights configurable — never a black box.
      </p>
      {data.length === 0 && <Empty text="No trends yet — run research first." />}
      {data.map((t) => (
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
