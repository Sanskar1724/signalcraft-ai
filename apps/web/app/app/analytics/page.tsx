"use client";

import { useState } from "react";
import { api } from "../../../lib/api";
import { Donut, HBar, Sparkline } from "../../../components/charts";
import { Card, Empty, Loading, Stat, Tabs, useApi } from "../../../components/ui";

const RANGES: Record<string, number> = { "7 days": 7, "30 days": 30, "90 days": 90, "All time": 100000 };

export default function AnalyticsPage() {
  const { data, error, busy, reload } = useApi(() => api.analytics());
  const [range, setRange] = useState("All time");

  if (busy) return (<><h1>Analytics</h1><Loading /></>);
  if (error || !data) return (<><h1>Analytics</h1><div className="error">We couldn&apos;t load analytics — your content is safe.
    <p><button className="btn small" onClick={reload}>Retry</button></p></div></>);

  const cutoff = Date.now() - RANGES[range] * 86400 * 1000;
  const inRange = (data.rows ?? []).filter((r) => {
    const t = new Date((r.recorded_at || "").replace(" ", "T") + "Z").getTime();
    return Number.isNaN(t) || t >= cutoff;
  });
  const rows = [...inRange].reverse();
  const tot = (k: "impressions" | "likes" | "comments" | "shares") =>
    inRange.reduce((a, r) => a + (r[k] || 0), 0);
  const engagement = tot("likes") + tot("comments") + tot("shares");
  const avg = inRange.length ? inRange.reduce((a, r) => a + r.engagement_rate, 0) / inRange.length : 0;
  const platMax = Math.max(...data.by_platform.map((x) => x.avg_engagement), 1);
  const weak = [...inRange].sort((a, b) => a.engagement_rate - b.engagement_rate).slice(0, 5);
  const byPlat: Record<string, number> = {};
  for (const r of inRange) byPlat[r.platform] = (byPlat[r.platform] || 0) + 1;

  return (
    <>
      <h1>Content Analytics</h1>
      <p className="sub">Understand what your audience actually responds to.</p>
      <Tabs tabs={Object.keys(RANGES)} active={range} onChange={setRange} />
      <div className="grid3" style={{ marginTop: 12 }}>
        <Stat hot value={String(inRange.length)} label="Posts in range" />
        <Stat value={String(tot("impressions"))} label="Impressions" />
        <Stat value={String(engagement)} label="Likes + comments + shares" />
      </div>
      <div className="grid3" style={{ marginTop: 12 }}>
        <Stat value={`${avg.toFixed(1)}%`} label="Avg engagement rate" />
        <Stat value={data.by_platform[0]?.platform ?? "—"} label="Best platform" />
        <Stat value={data.best_topics[0]?.topic ?? "—"} label="Best topic" />
      </div>
      <div className="grid2" style={{ marginTop: 12 }}>
        <Card>
          <h3>Performance over time</h3>
          <Sparkline points={rows.map((r) => r.engagement_rate)} w={480} h={110} />
          <p className="muted">Oldest → newest in range.</p>
        </Card>
        <Card>
          <h3>Posts by platform</h3>
          <Donut parts={Object.entries(byPlat).map(([label, value]) => ({ label, value }))} />
        </Card>
      </div>
      <div className="grid3">
        <Card>
          <h3>Score distribution</h3>
          <Donut parts={[
            { label: "Strong (8+)", value: inRange.filter((r) => r.performance_score >= 8).length },
            { label: "Solid (5-8)", value: inRange.filter((r) => r.performance_score >= 5 && r.performance_score < 8).length },
            { label: "Weak (<5)", value: inRange.filter((r) => r.performance_score < 5).length },
          ]} />
        </Card>
        <Card>
          <h3>Format performance</h3>
          {(data.by_format ?? []).map((t) => (
            <HBar key={t.format} label={`${t.format || "Unspecified"} (${t.posts})`} value={t.avg_engagement} max={platMax} />
          ))}
          {!(data.by_format ?? []).length && <p className="muted">No format data yet — set a format when creating.</p>}
        </Card>
        <Card>
          <h3>Best topics</h3>
          {data.best_topics.map((t) => (
            <HBar key={t.topic} label={`${t.topic} (${t.posts})`} value={t.avg_engagement} max={platMax} />
          ))}
          {!data.best_topics.length && <p className="muted">No data yet.</p>}
        </Card>
        <Card>
          <h3>Platform comparison</h3>
          {data.by_platform.map((t) => (
            <HBar key={t.platform} label={`${t.platform} (${t.posts})`} value={t.avg_engagement} max={platMax} />
          ))}
        </Card>
        <Card>
          <h3>Weak content</h3>
          {weak.map((r) => (
            <p key={r.id} className="muted">{r.title.slice(0, 60)} — {r.engagement_rate}%</p>
          ))}
          {!weak.length && <p className="muted">Nothing weak in range.</p>}
        </Card>
      </div>
      <Card>
        <h3>Platform comparison</h3>
        <div style={{ overflowX: "auto" }}>
          <table style={{ width: "100%", fontSize: 13, borderCollapse: "collapse" }}>
            <thead>
              <tr className="muted" style={{ textAlign: "left" }}>
                <th>Platform</th><th>Posts</th><th>Impressions</th><th>Avg engagement</th>
              </tr>
            </thead>
            <tbody>
              {Object.entries(
                inRange.reduce((acc, r) => {
                  const p = (acc[r.platform] ??= { posts: 0, imp: 0, er: 0 });
                  p.posts++;
                  p.imp += r.impressions || 0;
                  p.er += r.engagement_rate || 0;
                  return acc;
                }, {} as Record<string, { posts: number; imp: number; er: number }>)
              ).map(([plat, v]) => (
                <tr key={plat} style={{ borderTop: "1px solid var(--border)" }}>
                  <td><b>{plat}</b></td>
                  <td>{v.posts}</td>
                  <td>{v.imp}</td>
                  <td>{(v.er / Math.max(1, v.posts)).toFixed(1)}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
      <h2>Best-performing content</h2>      {(data.top_content ?? []).map((c) => (
        <Card key={c.id}><p style={{ margin: 0 }}><b>{c.title.slice(0, 80)}</b> — score {c.performance_score}</p></Card>
      ))}
      {data.posts === 0 && <Empty text="No performance data yet. Once you publish content and enter metrics, SignalCraft will learn what works best for you." />}
    </>
  );
}
