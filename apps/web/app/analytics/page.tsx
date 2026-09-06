"use client";

import { api } from "../../lib/api";
import { Card, Empty, Loading, ScoreBar, Stat, useApi } from "../../components/ui";

export default function AnalyticsPage() {
  const { data, error, busy } = useApi(() => api.analytics());

  if (busy) return (<><h1>Analytics</h1><Loading /></>);
  if (error || !data) return (<><h1>Analytics</h1><div className="error">API unavailable: {error}</div></>);

  return (
    <>
      <h1>Analytics</h1>
      <p className="sub">Engagement trend, best topics, formats and platforms.</p>
      <div className="grid3">
        <Stat hot value={String(data.posts)} label="Posts tracked" />
        <Stat value={`${data.avg_engagement}%`} label="Avg engagement" />
        <Stat value={data.by_platform[0]?.platform ?? "—"} label="Top platform" />
      </div>
      <div className="grid3" style={{ marginTop: 12 }}>
        <Card>
          <h3>Best topics</h3>
          {data.best_topics.map((t) => (
            <div key={t.topic}><p className="muted">{t.topic} — {t.avg_engagement}%</p><ScoreBar value={t.avg_engagement} max={Math.max(10, t.avg_engagement)} /></div>
          ))}
        </Card>
        <Card>
          <h3>Weak topics</h3>
          {data.weak_topics.map((t) => (
            <div key={t.topic}><p className="muted">{t.topic} — {t.avg_engagement}%</p><ScoreBar value={t.avg_engagement} max={Math.max(10, t.avg_engagement)} /></div>
          ))}
        </Card>
        <Card>
          <h3>Best formats</h3>
          {data.by_platform.map((t) => (
            <div key={t.platform}><p className="muted">{t.platform} — {t.avg_engagement}%</p><ScoreBar value={t.avg_engagement} max={Math.max(10, t.avg_engagement)} /></div>
          ))}
        </Card>
      </div>
      {data.posts === 0 && <Empty text="Log performance for a post to unlock analytics." />}
    </>
  );
}
