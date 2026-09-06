"use client";

import Link from "next/link";
import { api } from "../../lib/api";
import { HBar, Sparkline } from "../../components/charts";
import { timeAgo } from "../../components/charts";
import { Card, Empty, Loading, Pill, Quality, ScoreBar, Stat, useApi } from "../../components/ui";

export default function OverviewPage() {
  const a = useApi(() => api.analytics());
  const o = useApi(() => api.opportunities());
  const ins = useApi(() => api.insights());
  const me = useApi(() => api.me());
  const lib = useApi(() => api.library());
  const busy = a.busy || o.busy || ins.busy || lib.busy;
  const error = a.error || o.error || ins.error || lib.error;

  async function refresh() {
    await api.runResearch(20);
    a.reload();
    o.reload();
    ins.reload();
  }

  if (busy) return (<><h1>Overview</h1><Loading /></>);
  if (error || !a.data || !o.data || !lib.data)
    return (<><h1>Overview</h1><div className="error">API unavailable: {error} — is the backend running?</div></>);

  const top = o.data.slice(0, 3);
  const trend = (a.data.rows ?? []).map((r) => r.engagement_rate);
  const topPlatform = a.data.by_platform[0];
  const hour = new Date().getHours();
  const daypart = hour < 12 ? "morning" : hour < 17 ? "afternoon" : "evening";
  const first = (me.data?.user.name ?? "creator").split(" ")[0];

  return (
    <>
      <h1>Good {daypart}, {first}.</h1>
      <p className="sub">Here&apos;s what your content intelligence found today.</p>
      <div className="grid3">
        <Stat hot value={String(top.length)} label="Top opportunities" />
        <Stat value={String(a.data.posts)} label="Posts tracked" />
        <Stat value={`${a.data.avg_engagement}%`} label="Avg engagement" />
      </div>
      <div className="row" style={{ marginTop: 12 }}>
        <button className="btn ghost" onClick={refresh}>Refresh research</button>
        <Link href="/app/create" className="btn" style={{ textDecoration: "none" }}>Create content</Link>
        <Link href="/app/agent" className="btn ghost" style={{ textDecoration: "none" }}>Ask agent</Link>
      </div>

      <div className="grid3" style={{ marginTop: 4 }}>
        <Card>
          <h3>Engagement trend</h3>
          <Sparkline points={trend} />
          <p className="muted">Per-post engagement across your library.</p>
        </Card>
        <Card>
          <h3>Top topics</h3>
          {(a.data.best_topics ?? []).map((t) => (
            <HBar key={t.topic} label={t.topic} value={t.avg_engagement}
              max={Math.max(...a.data!.best_topics.map((x) => x.avg_engagement), 1)} />
          ))}
          {!(a.data.best_topics ?? []).length && <p className="muted">No data yet.</p>}
        </Card>
        <Card>
          <h3>Top platforms</h3>
          {(a.data.by_platform ?? []).slice(0, 4).map((t) => (
            <HBar key={t.platform} label={t.platform} value={t.avg_engagement}
              max={Math.max(...a.data!.by_platform.map((x) => x.avg_engagement), 1)} />
          ))}
          {topPlatform && <p className="muted">Prioritize {topPlatform.platform} this week.</p>}
        </Card>
      </div>

      <h2>Recent recommendations</h2>
      {top.length === 0 && <Empty text="No opportunities yet — hit Refresh research." />}
      {top.map((item) => (
        <Card key={item.id} glow>
          <h3>{item.topic} — {item.score}/100</h3>
          <ScoreBar value={item.score} />
          <p className="muted">{item.angle}</p>
          <p className="muted">Best for: {item.platform} · confidence {item.confidence}</p>
        </Card>
      ))}

      <h2>AI insights</h2>
      {(ins.data?.insights ?? []).slice(0, 3).map((l, i) => (
        <Card key={i}><p style={{ margin: 0 }}>{l}</p></Card>
      ))}
      <p><Link href="/app/insights" style={{ color: "var(--accent2)" }}>All insights →</Link></p>

      <h2>Recent content</h2>
      {lib.data.slice(0, 5).map((c) => (
        <Card key={c.id}>
          <div className="row" style={{ alignItems: "center" }}>
            <Pill kind={c.platform}>{c.platform}</Pill>
            <b>{c.title.slice(0, 80)}</b>
            <span style={{ flex: 1 }} />
            <Quality score={c.quality_score} />
          </div>
          <p className="muted">{c.status} · {timeAgo(c.created_at)}</p>
        </Card>
      ))}
      {!lib.data.length && <Empty text="No content yet — generate your first draft." />}
      <p><Link href="/app/library" style={{ color: "var(--accent2)" }}>Full library →</Link></p>
      <p className="stamp">Updated {timeAgo(new Date().toISOString())} · demo data</p>
    </>
  );
}
