"use client";

import { useState } from "react";
import { api, type ContentDetail, type ContentItem } from "../../lib/api";
import { timeAgo } from "../../components/charts";
import { Card, CopyButton, Empty, Loading, Modal, Pill, Quality, Tabs, useApi } from "../../components/ui";

export default function LibraryPage() {
  const lib = useApi(() => api.library());
  const [platform, setPlatform] = useState("All");
  const [query, setQuery] = useState("");
  const [openId, setOpenId] = useState<number | null>(null);
  const [detail, setDetail] = useState<ContentDetail | null>(null);
  const [perf, setPerf] = useState({ impressions: 1000, likes: 50, comments: 5, shares: 2, clicks: 2, saves: 3, reach: 800 });
  const [saved, setSaved] = useState("");

  const items = (lib.data ?? []).filter(
    (c) =>
      (platform === "All" || c.platform === platform) &&
      (!query || (c.title + (c as ContentItem & { topic?: string }).topic).toLowerCase().includes(query.toLowerCase()))
  );

  async function open(id: number) {
    setOpenId(id);
    setDetail(null);
    setSaved("");
    setDetail(await api.detail(id));
  }

  async function savePerf() {
    if (!openId) return;
    await api.logPerformance(openId, { platform: detail?.platform, ...perf });
    setSaved("Saved — insights and memory updated.");
    lib.reload();
    setDetail(await api.detail(openId));
  }

  if (lib.busy) return (<><h1>Content Library</h1><Loading /></>);
  if (lib.error || !lib.data) return (<><h1>Content Library</h1><div className="error">API unavailable: {lib.error}</div></>);

  return (
    <>
      <h1>Content Library</h1>
      <p className="sub">{lib.data.length} pieces · click any row for body, versions and performance.</p>
      <div className="row">
        <div style={{ flex: 2, minWidth: 220 }}>
          <input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Search titles…" />
        </div>
        <Tabs tabs={["All", "LinkedIn", "X", "Blog"]} active={platform} onChange={setPlatform} />
      </div>
      {items.length === 0 && <Empty text="Nothing matches — clear the filters." />}
      {items.map((c) => (
        <Card key={c.id}>
          <div className="row" style={{ alignItems: "center", cursor: "pointer" }} onClick={() => open(c.id)}>
            <Pill kind={c.platform}>{c.platform}</Pill>
            <b>{c.title}</b>
            <span style={{ flex: 1 }} />
            <Quality score={c.quality_score} />
          </div>
          <p className="muted">{c.status} · {timeAgo(c.created_at)}</p>
        </Card>
      ))}

      <Modal open={openId !== null} onClose={() => setOpenId(null)} title={detail?.title ?? "Loading…"}>
        {!detail && <Loading />}
        {detail && (
          <>
            <div className="row" style={{ alignItems: "center" }}>
              <Pill kind={detail.platform}>{detail.platform}</Pill>
              <Quality score={detail.quality_score} />
              <span style={{ flex: 1 }} />
              <CopyButton text={detail.body} />
            </div>
            <pre className="draft">{detail.body}</pre>
            <h2>Versions ({detail.versions.length})</h2>
            {detail.versions.map((v) => (
              <p key={v.version} className="muted">v{v.version} — score {v.score} · {timeAgo(v.created_at)}</p>
            ))}
            <h2>Performance</h2>
            {detail.performance?.impressions ? (
              <p className="muted">
                {detail.performance.impressions} impressions · {detail.performance.engagement_rate}% engagement ·
                score {detail.performance.performance_score}
              </p>
            ) : (
              <p className="muted">No metrics yet — log them below.</p>
            )}
            <h2>Log performance</h2>
            <div className="grid3">
              {(["impressions", "reach", "likes", "comments", "shares", "clicks", "saves"] as const).map((k) => (
                <label className="field" key={k} style={{ minWidth: 120 }}>{k}
                  <input type="number" value={perf[k]} onChange={(e) => setPerf({ ...perf, [k]: Number(e.target.value) })} />
                </label>
              ))}
            </div>
            <p><button className="btn small" onClick={savePerf}>Save metrics</button></p>
            {saved && <p className="muted">{saved}</p>}
          </>
        )}
      </Modal>
    </>
  );
}
