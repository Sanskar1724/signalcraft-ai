"use client";

import { useState } from "react";
import { api } from "../../lib/api";
import { Card, Loading, useApi } from "../../components/ui";

function split(lines: string[]) {
  const good: string[] = [];
  const bad: string[] = [];
  const next: string[] = [];
  for (const l of lines) {
    if (/weak|pause|reframe/i.test(l)) bad.push(l);
    else if (/best|strong|prioritize|more of this/i.test(l)) good.push(l);
    else next.push(l);
  }
  return { good, bad, next };
}

export default function InsightsPage() {
  const ins = useApi(() => api.insights());
  const mem = useApi(() => api.memories());
  const [learned, setLearned] = useState("");
  const busy = ins.busy || mem.busy;
  const error = ins.error || mem.error;

  async function learn() {
    setLearned("");
    const r = await api.learn();
    setLearned(r.learned.length ? `Stored: ${r.learned.join("; ")}` : "Nothing new to store.");
    mem.reload();
  }

  if (busy) return (<><h1>AI Insights</h1><Loading /></>);
  if (error) return (<><h1>AI Insights</h1><div className="error">API unavailable: {error}</div></>);

  const { good, bad, next } = split(ins.data?.insights ?? []);

  return (
    <>
      <h1>What should you change?</h1>
      <p className="sub">Derived from your performance — then stored as durable memory.</p>
      <p><button className="btn ghost" onClick={learn}>Learn from performance → memory</button></p>
      {learned && <p className="muted">{learned}</p>}
      <h2>What is working</h2>
      {good.map((l, i) => (<Card key={i} glow><p style={{ margin: 0 }}>{l}</p></Card>))}
      {!good.length && <p className="muted">Nothing conclusive yet.</p>}
      <h2>What is not working</h2>
      {bad.map((l, i) => (<Card key={i}><p style={{ margin: 0 }}>{l}</p></Card>))}
      {!bad.length && <p className="muted">No weak spots detected.</p>}
      <h2>What to try next</h2>
      {next.map((l, i) => (<Card key={i}><p style={{ margin: 0 }}>{l}</p></Card>))}
      <h2>Creator memory</h2>
      {(mem.data?.memories ?? []).map((m, i) => (
        <p key={i} className="muted">
          <span className="pill">{m.kind}</span> <b style={{ color: "var(--text)" }}>{m.key}</b> — {m.value} (hits {m.hits})
        </p>
      ))}
      {(mem.data?.memories ?? []).length === 0 && <p className="muted">Memory fills as you log performance.</p>}
    </>
  );
}
