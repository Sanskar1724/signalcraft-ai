"use client";

import { useState } from "react";
import { api } from "../../lib/api";
import { Card } from "../../components/ui";

const SUGGESTIONS = [
  "What should I post today?",
  "Give me the top 3 opportunities for my niche.",
  "Why did my last post perform poorly?",
  "Give me a technical angle.",
  "What topics are currently rising?",
];

export default function AgentPage() {
  const [q, setQ] = useState("");
  const [log, setLog] = useState<{ me: string; bot: string }[]>([]);
  const [busy, setBusy] = useState(false);

  async function ask(text: string) {
    const msg = text.trim();
    if (!msg || busy) return;
    setQ("");
    setBusy(true);
    try {
      const r = await api.chat(msg);
      setLog((l) => [...l, { me: msg, bot: r.answer }]);
    } catch (e) {
      setLog((l) => [...l, { me: msg, bot: `Error: ${(e as Error).message}` }]);
    } finally {
      setBusy(false);
    }
  }

  return (
    <>
      <h1>Ask your content agent</h1>
      <p className="sub">Answers come from your data and tools — never model knowledge alone.</p>
      <div className="row">
        {SUGGESTIONS.map((s) => (
          <button key={s} className="btn ghost small" onClick={() => ask(s)}>{s}</button>
        ))}
      </div>
      <div className="thread">
        {log.map((m, i) => (
          <div key={i} style={{ display: "contents" }}>
            <div className="bubble me">{m.me}</div>
            <div className="bubble"><pre>{m.bot}</pre></div>
          </div>
        ))}
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
