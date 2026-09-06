"use client";

import { useEffect, useState } from "react";
import { api, type Memory } from "../../lib/api";

export default function InsightsPage() {
  const [lines, setLines] = useState<string[]>([]);
  const [mems, setMems] = useState<Memory[]>([]);

  useEffect(() => {
    api.insights().then((r) => setLines(r.insights)).catch(() => setLines([]));
    api.memories().then((r) => setMems(r.memories)).catch(() => setMems([]));
  }, []);

  return (
    <>
      <h1>What should you change?</h1>
      {lines.map((l, i) => (
        <p key={i}>- {l}</p>
      ))}
      <h2>Creator memory</h2>
      {mems.map((m, i) => (
        <p key={i} className="muted">
          <code>{m.kind}</code> <b>{m.key}</b> — {m.value} (hits {m.hits})
        </p>
      ))}
    </>
  );
}
