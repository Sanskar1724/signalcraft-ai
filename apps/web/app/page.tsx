"use client";

import { useEffect, useState } from "react";
import { api, type AnalyticsSummary, type Opportunity } from "../lib/api";

export default function OverviewPage() {
  const [data, setData] = useState<AnalyticsSummary | null>(null);
  const [opps, setOpps] = useState<Opportunity[]>([]);
  const [error, setError] = useState("");

  useEffect(() => {
    Promise.all([api.analytics(), api.opportunities()])
      .then(([a, o]) => {
        setData(a);
        setOpps(o.slice(0, 3));
      })
      .catch((e) => setError(e.message));
  }, []);

  if (error) return <p className="error">API unavailable: {error} — start the API first.</p>;
  if (!data) return <p>Loading…</p>;

  return (
    <>
      <h1>What should you talk about right now?</h1>
      <div className="grid3">
        <div className="metric"><b>{opps.length}</b>Top opportunities</div>
        <div className="metric"><b>{data.posts}</b>Posts tracked</div>
        <div className="metric"><b>{data.avg_engagement}%</b>Avg engagement</div>
      </div>
      <h2>Top recommendations</h2>
      {opps.length === 0 && <p className="muted">No opportunities yet. Run research first.</p>}
      {opps.map((o) => (
        <div key={o.id} className="card">
          <b>{o.topic}</b> — {o.score}/100 · conf {o.confidence}
          <p className="muted">Why now: {o.why_now}</p>
          <p className="muted">Why you: {o.why_you}</p>
        </div>
      ))}
    </>
  );
}
