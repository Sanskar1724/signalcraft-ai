"use client";

import { api } from "../../lib/api";
import { Card, Loading, useApi } from "../../components/ui";

export default function InsightsPage() {
  const ins = useApi(() => api.insights());
  const mem = useApi(() => api.memories());
  const busy = ins.busy || mem.busy;
  const error = ins.error || mem.error;

  if (busy) return (<><h1>AI Insights</h1><Loading /></>);
  if (error) return (<><h1>AI Insights</h1><div className="error">API unavailable: {error}</div></>);

  return (
    <>
      <h1>What should you change?</h1>
      <p className="sub">Derived from your performance — then stored as memory.</p>
      {(ins.data?.insights ?? []).map((l, i) => (
        <Card key={i} glow={i === 0}><p style={{ margin: 0 }}>{l}</p></Card>
      ))}
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
