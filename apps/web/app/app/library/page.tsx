"use client";

import { useState } from "react";
import { api, type ContentDetail, type ContentItem } from "../../../lib/api";
import { toast } from "../../../components/fx";
import { timeAgo } from "../../../components/charts";
import { Card, CopyButton, Empty, Loading, Modal, Pill, Quality, Tabs, useApi } from "../../../components/ui";

export default function LibraryPage() {
  const lib = useApi(() => api.library());
  const [platform, setPlatform] = useState("All");
  const [status, setStatus] = useState("All");
  const [query, setQuery] = useState("");
  const [openId, setOpenId] = useState<number | null>(null);
  const [detail, setDetail] = useState<ContentDetail | null>(null);
  const [perf, setPerf] = useState({ impressions: 1000, likes: 50, comments: 5, shares: 2, clicks: 2, saves: 3, reach: 800 });
  const [saved, setSaved] = useState("");
  const [view, setView] = useState("List");
  const [sel, setSel] = useState<Set<number>>(new Set());

  function toggleSel(id: number) {
    setSel((s) => {
      const n = new Set(s);
      if (n.has(id)) n.delete(id);
      else n.add(id);
      return n;
    });
  }

  async function bulk(status: string) {
    const ids = Array.from(sel);
    for (const id of ids) {
      await api.setStatus(id, status);
    }
    toast(`${ids.length} item(s) → ${status}.`);
    setSel(new Set());
    lib.reload();
  }

  async function bulkDelete() {
    const ids = Array.from(sel);
    for (const id of ids) {
      await api.removeContent(id);
    }
    toast(`${ids.length} item(s) deleted.`);
    setSel(new Set());
    lib.reload();
  }

  async function duplicate(id: number) {
    await api.duplicateContent(id);
    toast("Duplicated as a new draft.");
    lib.reload();
  }

  const items = (lib.data ?? []).filter(
    (c) =>
      (platform === "All" || c.platform === platform) &&
      (status === "All" || c.status === status) &&
      (!query || (c.title + " " + c.hook + " " + ((c as ContentItem & { opportunity_topic?: string }).opportunity_topic ?? "")).toLowerCase().includes(query.toLowerCase()))
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
        <Tabs tabs={["All", "LinkedIn", "X", "Blog", "Newsletter"]} active={platform} onChange={setPlatform} />
      </div>
      <div className="row" style={{ marginTop: 8 }}>
        <span className="lbl">Status</span>
        <Tabs tabs={["All", "draft", "ready", "published", "archived"]} active={status} onChange={setStatus} />
        <span style={{ flex: 1 }} />
        <Tabs tabs={["List", "Grid", "Timeline"]} active={view} onChange={setView} />
      </div>
      {sel.size > 0 && (
        <div className="row" style={{ marginTop: 8 }}>
          <span className="muted">{sel.size} selected</span>
          {(["draft", "ready", "published", "archived"] as const).map((s) => (
            <button key={s} className="btn ghost small" onClick={() => bulk(s)}>→ {s}</button>
          ))}
          <button className="btn ghost small" onClick={bulkDelete}>Delete</button>
          <button className="btn ghost small" onClick={() => setSel(new Set())}>Clear</button>
        </div>
      )}
      {items.length === 0 && <Empty text="Nothing matches — clear the filters." />}
      {view === "Timeline" ? (
        <div>
          {items.map((c) => (
            <div key={c.id} className="row" style={{ alignItems: "flex-start", flexWrap: "nowrap" }}>
              <span className="muted" style={{ minWidth: 110 }}>{timeAgo(c.created_at)}</span>
              <span className="navdot" style={{ marginTop: 6 }} />
              <div style={{ flex: 1 }}>
                <Card key={c.id} lift>
                  <div className="row" style={{ alignItems: "center", cursor: "pointer" }} onClick={() => open(c.id)}>
                    <Pill kind={c.platform}>{c.platform}</Pill>
                    <b>{c.title}</b>
                    <span style={{ flex: 1 }} />
                    <Quality score={c.quality_score} />
                  </div>
                  <p className="muted">{c.status}</p>
                </Card>
              </div>
            </div>
          ))}
        </div>
      ) : (
      <div className={view === "Grid" ? "grid2" : ""}>
      {items.map((c) => (
        <Card key={c.id} lift>
          <div className="row" style={{ alignItems: "center" }}>
            <input type="checkbox" aria-label={`Select ${c.title}`} checked={sel.has(c.id)}
              onChange={() => toggleSel(c.id)} style={{ width: 18 }} />
            <div className="row" style={{ alignItems: "center", cursor: "pointer", flex: 1 }} onClick={() => open(c.id)}>
              <Pill kind={c.platform}>{c.platform}</Pill>
              <b>{c.title}</b>
              <span style={{ flex: 1 }} />
              <Quality score={c.quality_score} />
            </div>
          </div>
          <p className="muted">{c.status} · {timeAgo(c.created_at)}</p>
          <div className="row">
            <button className="btn ghost small" onClick={() => duplicate(c.id)}>Duplicate</button>
          </div>
        </Card>
      ))}
      </div>
      )}

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
            <div className="row" style={{ marginTop: 8 }}>
              <span className="lbl">Move to</span>
              {["draft", "ready", "published", "archived"].map((s) => (
                <button key={s} className="btn ghost small"
                  onClick={async () => {
                    await api.setStatus(detail.id, s);
                    setDetail(await api.detail(detail.id));
                    lib.reload();
                  }}>
                  {s}
                </button>
              ))}
            </div>
            <pre className="draft">{detail.body}</pre>
            <h2>Versions ({detail.versions.length})</h2>
            {detail.versions.map((v) => (
              <details className="trace" key={v.version}>
                <summary>v{v.version} — score {v.score} · {timeAgo(v.created_at)}</summary>
                <pre className="draft">{v.body}</pre>
              </details>
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
