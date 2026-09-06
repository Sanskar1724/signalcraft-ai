"use client";

import { useEffect, useState } from "react";
import { api, type TrendSignal } from "../../lib/api";

export default function TrendingPage() {
  const [trends, setTrends] = useState<TrendSignal[]>([]);
  const [error, setError] = useState("");

  useEffect(() => {
    api.trends().then(setTrends).catch((e) => setError(e.message));
  }, []);

  if (error) return <p className="error">API unavailable: {error}</p>;

  return (
    <>
      <h1>Trending — filtered for you</h1>
      <p className="muted">
        Trend score = 30% growth + 25% freshness + 20% relevance + 15% source momentum + 10%
        novelty. Weights configurable.
      </p>
      {trends.map((t) => (
        <div key={t.topic} className="card">
          <b>{t.topic}</b> — {t.trend_score}
          <p className="muted">
            Freshness {t.freshness} · Growth {t.growth} · Relevance {t.relevance} · Momentum{" "}
            {t.source_momentum} · Novelty {t.novelty} · Audience {t.audience_fit} · Competition{" "}
            {t.competition}
          </p>
        </div>
      ))}
      {trends.length === 0 && <p className="muted">No trends yet.</p>}
    </>
  );
}
