"use client";

import { useState } from "react";
import { api, type ContentDetail, type ContentItem } from "../../../lib/api";
import { toast } from "../../../components/fx";
import { timeAgo } from "../../../components/charts";
import { Card, CopyButton, Empty, Loading, Modal, Pill, Quality, Stat, Tabs, useApi } from "../../../components/ui";

function Diff({ oldText, newText }: { oldText: string; newText: string }) {
  // Word-level LCS diff: green = added, red = removed.
  const a = oldText.split(/\s+/);
  const b = newText.split(/\s+/);
  const cap = 400;
  const A = a.slice(0, cap);
  const B = b.slice(0, cap);
  const dp: number[][] = Array.from({ length: A.length + 1 }, () => new Array(B.length + 1).fill(0));
  for (let i = A.length - 1; i >= 0; i--) {
    for (let j = B.length - 1; j >= 0; j--) {
      dp[i][j] = A[i] === B[j] ? dp[i + 1][j + 1] + 1 : Math.max(dp[i + 1][j], dp[i][j + 1]);
    }
  }
  const out: { t: string; k: string }[] = [];
  let i = 0;
  let j = 0;
  let guard = 0;
  while ((i < A.length || j < B.length) && guard++ < 2000) {
    if (i < A.length && j < B.length && A[i] === B[j]) {
      out.push({ t: A[i], k: "=" });
      i++;
      j++;
    } else if (j < B.length && (i >= A.length || dp[i][j + 1] >= dp[i + 1][j])) {
      out.push({ t: B[j], k: "+" });
      j++;
    } else {
      out.push({ t: A[i], k: "-" });
      i++;
    }
  }
  return (
    <p className="draft" style={{ fontSize: 13 }}>
      {out.slice(0, 600).map((w, k) =>
        w.k === "=" ? <span key={k}>{w.t} </span>
        : w.k === "+" ? <ins key={k} className="diff">{w.t} </ins>
        : <del key={k} className="diff">{w.t} </del>
      )}
    </p>
  );
}

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
  const [minScore, setMinScore] = useState(0);
  const [days, setDays] = useState("All time");
  const [topic, setTopic] = useState("All topics");
  const [compare, setCompare] = useState<number | null>(null);

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

  const topics = Array.from(new Set((lib.data ?? []).map(
    (c) => (c as ContentItem & { opportunity_topic?: string }).opportunity_topic).filter(Boolean))) as string[];
  const items = (lib.data ?? []).filter(
    (c) =>
      (platform === "All" || c.platform === platform) &&
      (status === "All" || c.status === status) &&
      c.quality_score >= minScore &&
      (topic === "All topics" || ((c as ContentItem & { opportunity_topic?: string }).opportunity_topic ?? "") === topic) &&
      (days === "All time" || Date.now() - new Date(c.created_at.replace(" ", "T") + "Z").getTime() < (days === "Last 7 days" ? 7 : 30) * 86400000) &&
      (!query || (c.title + " " + c.hook + " " + ((c as ContentItem & { opportunity_topic?: string }).opportunity_topic ?? "")).toLowerCase().includes(query.toLowerCase()))
  );
  const counts = (s: string) => (lib.data ?? []).filter((c) => s === "All" ? true : c.status === s).length;
  const avgScore = lib.data?.length
    ? (lib.data.reduce((a, c) => a + c.quality_score, 0) / lib.data.length).toFixed(1) : "—";

  async function open(id: number) {
    setOpenId(id);
    setDetail(null);
    setSaved("");
    setCompare(null);
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
      <div className="grid3">
        <Stat value={String(lib.data.length)} label="Total" />
        <Stat value={`${counts("draft")}/${counts("ready")}/${counts("published")}`} label="Draft / Ready / Published" />
        <Stat value={String(avgScore)} label="Avg quality score" />
      </div>
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
      <div className="row" style={{ marginTop: 8 }}>
        <label className="field" style={{ minWidth: 130, flex: 0 }}>Min score
          <select value={minScore} onChange={(e) => setMinScore(Number(e.target.value))}>
            {[0, 6, 7, 8, 9].map((s) => <option key={s} value={s}>{s === 0 ? "Any" : `${s}+`}</option>)}
          </select>
        </label>
        <label className="field" style={{ minWidth: 150, flex: 0 }}>Topic
          <select value={topic} onChange={(e) => setTopic(e.target.value)}>
            <option>All topics</option>
            {topics.map((t) => <option key={t}>{t}</option>)}
          </select>
        </label>
        <Tabs tabs={["All time", "Last 7 days", "Last 30 days"]} active={days} onChange={setDays} />
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
            {detail.versions.map((v, vi) => (
              <details className="trace" key={v.version}>
                <summary>v{v.version} — score {v.score} · {timeAgo(v.created_at)}</summary>
                <pre className="draft">{v.body}</pre>
                {vi > 0 && (
                  <div className="row" style={{ marginTop: 6 }}>
                    <button className="btn ghost small"
                      onClick={() => setCompare(compare === v.version ? null : v.version)}>
                      {compare === v.version ? "Hide changes" : "Compare with previous"}
                    </button>
                    <button className="btn ghost small" onClick={async () => {
                      await api.restore(detail.id, v.version);
                      toast(`Restored v${v.version} as a new version.`);
                      setDetail(await api.detail(detail.id));
                      lib.reload();
                    }}>
                      Restore this version
                    </button>
                  </div>
                )}
                {compare === v.version && vi > 0 && (
                  <Diff oldText={detail.versions[vi - 1].body} newText={v.body} />
                )}
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
