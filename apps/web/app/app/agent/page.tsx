"use client";

import Link from "next/link";
import { useState } from "react";
import { api } from "../../../lib/api";
import { Card, Loading, useApi } from "../../../components/ui";

const SUGGESTIONS = [
  "What should I post today?",
  "Give me the top 3 opportunities for my niche.",
  "Why did my last post perform poorly?",
  "Give me a technical angle.",
  "What topics are currently rising?",
  "What type of content works best for me?",
];

function stamp() {
  return new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

const STAGE_LABELS: Record<string, string> = {
  understand_request: "Understanding request",
  creator_context: "Loading creator context",
  memory: "Checking memory",
  "tool:research.search": "Researching current signals",
  "tool:opportunities.list": "Ranking opportunities",
  "tool:analytics.summary": "Analyzing performance",
  "tool:analytics.insights": "Generating strategy",
  "tool:content.generate": "Generating strategy",
  opportunity_selected: "Opportunity selected",
};

function stageLabel(stage: string) {
  if (STAGE_LABELS[stage]) return STAGE_LABELS[stage];
  if (stage.startsWith("tool:")) return stage.slice(5).replace(/_/g, " ");
  if (stage.startsWith("tool_error")) return "Recovered from a tool hiccup";
  return stage.replace(/_/g, " ");
}

export default function AgentPage() {
  const [q, setQ] = useState("");
  const [log, setLog] = useState<{ me: string; at: string; bot: string;
    actions: { label: string; href: string }[]; trace: { stage: string }[] }[]>([]);
  const [busy, setBusy] = useState(false);
  const ctx = useApi(() => api.context());
  const trends = useApi(() => api.trends(3));
  const opps = useApi(() => api.opportunities());

  async function ask(text: string) {
    const msg = text.trim();
    if (!msg || busy) return;
    setQ("");
    setBusy(true);
    try {
      const r = await api.chat(msg);
      setLog((l) => [...l, { me: msg, at: stamp(), bot: r.answer, actions: r.actions ?? [], trace: r.trace?.steps ?? [] }]);
    } catch (e) {
      setLog((l) => [...l, { me: msg, at: stamp(), bot: `Error: ${(e as Error).message}`, actions: [], trace: [] }]);
    } finally {
      setBusy(false);
    }
  }

  return (
    <>
      <h1>Agent</h1>
      <p className="sub">Your strategist, with its working context beside it.</p>
      <div className="workgrid">
        <div>
          <div className="row">
            {SUGGESTIONS.map((s) => (
              <button key={s} className="btn ghost small" onClick={() => ask(s)}>{s}</button>
            ))}
          </div>
          <div className="thread">
            {log.map((m, i) => (
              <div key={i} style={{ display: "contents" }}>
                <div className="bubble me">{m.me}<div className="stamp">{m.at}</div></div>
            <div className="bubble">
              <pre>{m.bot}</pre>
              <div className="stamp">{m.at}</div>
              {m.actions.length > 0 && (
                <div className="row" style={{ marginTop: 8 }}>
                  {m.actions.map((a) => (
                    <Link key={a.href + a.label} href={a.href} className="btn small" style={{ textDecoration: "none" }}>
                      {a.label}
                    </Link>
                  ))}
                </div>
              )}
              {m.trace.length > 0 && (
                <details className="trace">
                  <summary>How I got this ({m.trace.length} steps)</summary>
                  {m.trace.map((s, j) => (
                    <p key={j} className="muted">✓ {stageLabel(s.stage)}</p>
                  ))}
                </details>
              )}
                </div>
              </div>
            ))}
            {busy && <div className="bubble"><span className="spin" />Consulting your data…</div>}
            {!log.length && !busy && <p className="muted">Ask anything — answers come from your data and tools.</p>}
          </div>
          <Card>
            <div className="row">
              <label className="field">Question
                <input value={q} onChange={(e) => setQ(e.target.value)}
                  placeholder="What should I post today?"
                  onKeyDown={(e) => e.key === "Enter" && ask(q)} />
              </label>
            </div>
            <p style={{ marginBottom: 0 }}>
              <button className="btn" onClick={() => ask(q)} disabled={busy || !q.trim()}>
                {busy ? <><span className="spin" />Thinking…</> : "Ask"}
              </button>
            </p>
          </Card>
        </div>
        <Card>
          <h3>Context panel</h3>
          {ctx.busy && <p className="muted">Loading…</p>}
          {ctx.data && (
            <>
              <p className="lbl">Your niche</p>
              <p>{String(ctx.data.niche || "—")}</p>
              <p className="lbl">Posts · avg engagement</p>
              <p>{String(ctx.data.posts)} · {String(ctx.data.avg_engagement)}%</p>
              <p className="lbl">Current trends</p>
              {(trends.data ?? []).map((t) => (
                <p key={t.topic} className="muted">{t.topic} — {t.trend_score}</p>
              ))}
              <p className="lbl">Recommended</p>
              {(opps.data ?? []).slice(0, 3).map((o) => (
                <p key={o.id} className="muted">{o.topic} — {o.score}</p>
              ))}
            </>
          )}
          {ctx.error && <p className="muted">Context unavailable.</p>}
        </Card>
      </div>
    </>
  );
}
