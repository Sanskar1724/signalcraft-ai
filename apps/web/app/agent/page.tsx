"use client";

import { useState } from "react";
import { api } from "../../lib/api";

export default function AgentPage() {
  const [q, setQ] = useState("");
  const [answer, setAnswer] = useState("");
  const [busy, setBusy] = useState(false);

  async function ask() {
    setBusy(true);
    try {
      const r = await api.chat(q);
      setAnswer(r.answer);
    } catch (e) {
      setAnswer(`Error: ${(e as Error).message}`);
    } finally {
      setBusy(false);
    }
  }

  return (
    <>
      <h1>Ask your content agent</h1>
      <p className="muted">
        Try: What should I post today? · Why did my last post perform poorly? · Analyze my last
        10 posts · Make this less generic.
      </p>
      <input value={q} onChange={(e) => setQ(e.target.value)} placeholder="Question" />
      <p><button onClick={ask} disabled={busy || !q}>{busy ? "Thinking…" : "Ask"}</button></p>
      {answer && (
        <div className="card"><pre style={{ whiteSpace: "pre-wrap" }}>{answer}</pre></div>
      )}
    </>
  );
}
