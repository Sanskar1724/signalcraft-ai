"use client";

import { api } from "../../../lib/api";
import { HBar, Sparkline } from "../../../components/charts";
import { Card, Empty, Loading, Stat, useApi } from "../../../components/ui";

export default function AnalyticsPage() {
  const { data, error, busy } = useApi(() => api.analytics());

  if (busy) return (<><h1>Analytics</h1><Loading /></>);
  if (error || !data) return (<><h1>Analytics</h1><div className="error">API unavailable: {error}</div></>);

  const rows = [...(data.rows ?? [])].reverse();
  const platMax = Math.max(...data.by_platform.map((x) => x.avg_engagement), 1);
  const weak = [...(data.rows ?? [])].sort((a, b) => a.engagement_rate - b.engagement_rate).slice(0, 5);

  return (
    <>
      <h1>Analytics</h1>
      <p className="sub">Engagement trend, best topics, formats, platforms — and weak spots.</p>
      <div className="grid3">
        <Stat hot value={String(data.posts)} label="Posts tracked" />
        <Stat value={`${data.avg_engagement}%`} label="Avg engagement" />
        <Stat value={data.by_platform[0]?.platform ?? "—"} label="Top platform" />
      </div>
      <Card>
        <h3>Engagement trend</h3>
        <Sparkline points={rows.map((r) => r.engagement_rate)} w={640} h={110} />
        <p className="muted">Oldest → newest across your library.</p>
      </Card>
      <div className="grid3">
        <Card>
          <h3>Best topics</h3>
          {data.best_topics.map((t) => (
            <HBar key={t.topic} label={`${t.topic} (${t.posts})`} value={t.avg_engagement} max={platMax} />
          ))}
        </Card>
        <Card>
          <h3>Best formats</h3>
          {data.by_platform.map((t) => (
            <HBar key={t.platform} label={`${t.platform} (${t.posts})`} value={t.avg_engagement} max={platMax} />
          ))}
        </Card>
        <Card>
          <h3>Weak-performing content</h3>
          {weak.map((r) => (
            <p key={r.id} className="muted">{r.title.slice(0, 60)} — {r.engagement_rate}%</p>
          ))}
        </Card>
      </div>
      <h2>Best-performing content</h2>
      {(data.top_content ?? []).map((c) => (
        <Card key={c.id}><p style={{ margin: 0 }}><b>{c.title.slice(0, 80)}</b> — score {c.performance_score}</p></Card>
      ))}
      {data.posts === 0 && <Empty text="Log performance for a post to unlock analytics." />}
    </>
  );
}
