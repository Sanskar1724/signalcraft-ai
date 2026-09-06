"use client";

import { useState } from "react";
import { api } from "../../../lib/api";
import { Card } from "../../../components/ui";

const SUGGESTIONS = [
  "What should I post today?",
  "Give me the top 3 opportunities for my niche.",
  "Why did my last post perform poorly?",
  "Give me a technical angle.",
  "What topics are currently rising?",
];

function stamp() {
  return new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

export default function AgentPage() {
  const [q, setQ] = useState("");
  const [log, setLog] = useState<{ me: string; at: string; bot: string; trace: { stage: string }[] }[]>([]);
  const [busy, setBusy] = useState(false);

  async function ask(text: string) {
    const msg = text.trim();
    if (!msg || busy) return;
    setQ("");
    setBusy(true);
    try {
      const r = await api.chat(msg);
      setLog((l) => [...l, { me: msg, at: stamp(), bot: r.answer, trace: r.trace?.steps ?? [] }]);
    } catch (e) {
      setLog((l) => [...l, { me: msg, at: stamp(), bot: `Error: ${(e as Error).message}`, trace: [] }]);
    } finally {
      setBusy(false);
    }
  }

  return (
    <>
      <h1>Ask your content agent</h1>
      <p className="sub">Answers come from your data and tools — expand any reply to see exactly what the agent did.</p>
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
              {m.trace.length > 0 && (
                <details className="trace">
                  <summary>Execution trace ({m.trace.length} steps)</summary>
                  {m.trace.map((s, j) => (
                    <p key={j} className="muted">· {s.stage}</p>
                  ))}
                </details>
              )}
            </div>
          </div>
        ))}
        {busy && <div className="bubble"><span className="spin" />Consulting your data…</div>}
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
    </>
  );
}
