"use client";

import { useEffect, useState } from "react";
import { api, type Opportunity } from "../../lib/api";

export default function OpportunitiesPage() {
  const [opps, setOpps] = useState<Opportunity[]>([]);
  const [error, setError] = useState("");

  useEffect(() => {
    api.opportunities().then(setOpps).catch((e) => setError(e.message));
  }, []);

  if (error) return <p className="error">API unavailable: {error}</p>;

  return (
    <>
      <h1>Personalized opportunities</h1>
      {opps.map((o) => (
        <div key={o.id} className="card">
          <h3>
            {o.topic} — {o.score}/100
          </h3>
          <p className="muted">
            Trend {o.trend_score} · Relevance {o.user_relevance} · Audience {o.audience_fit} ·
            Freshness {o.freshness} · Competition {o.competition}
          </p>
          <p><b>Observed fact.</b> {o.why_now}</p>
          <p><b>AI interpretation.</b> {o.why_you}</p>
          <p><b>AI recommendation.</b> Angle: {o.angle}</p>
          <p className="muted">
            Audience: {o.audience} · Platform: {o.platform} · Confidence {o.confidence}
          </p>
        </div>
      ))}
      {opps.length === 0 && <p className="muted">No opportunities yet.</p>}
    </>
  );
}
