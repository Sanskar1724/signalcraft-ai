"use client";

import Link from "next/link";
import { api } from "../lib/api";
import { Card, Empty, Loading, ScoreBar, Stat, useApi } from "../components/ui";

export default function OverviewPage() {
  const a = useApi(() => api.analytics());
  const o = useApi(() => api.opportunities());
  const busy = a.busy || o.busy;
  const error = a.error || o.error;

  async function refresh() {
    await api.runResearch(20);
    a.reload();
    o.reload();
  }

  if (busy) return (<><h1>Overview</h1><Loading /></>);
  if (error || !a.data || !o.data)
    return (<><h1>Overview</h1><div className="error">API unavailable: {error} — is the backend running on :8000?</div></>);

  const top = o.data.slice(0, 3);
  return (
    <>
      <h1>What should you talk about right now?</h1>
      <p className="sub">Personalized briefing from your research, trends and performance.</p>
      <div className="grid3">
        <Stat hot value={String(top.length)} label="Top opportunities" />
        <Stat value={String(a.data.posts)} label="Posts tracked" />
        <Stat value={`${a.data.avg_engagement}%`} label="Avg engagement" />
      </div>
      <div className="row" style={{ marginTop: 12 }}>
        <button className="btn ghost" onClick={refresh}>Refresh research</button>
        <Link href="/create" className="btn" style={{ textDecoration: "none" }}>Create content</Link>
      </div>
      <h2>Top recommendations</h2>
      {top.length === 0 && <Empty text="No opportunities yet — hit Refresh research." />}
      {top.map((item) => (
        <Card key={item.id} glow>
          <h3>{item.topic} — {item.score}/100</h3>
          <ScoreBar value={item.score} />
          <p className="muted">{item.angle}</p>
          <p className="muted">Best for: {item.platform} · confidence {item.confidence}</p>
        </Card>
      ))}
    </>
  );
}
