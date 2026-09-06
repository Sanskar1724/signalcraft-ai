"use client";

import { useEffect, useState } from "react";
import { api, type GenerateResult, type Opportunity } from "../../lib/api";

export default function CreatePage() {
  const [opps, setOpps] = useState<Opportunity[]>([]);
  const [oppId, setOppId] = useState(0);
  const [platform, setPlatform] = useState("LinkedIn");
  const [result, setResult] = useState<GenerateResult | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    api.opportunities().then((o) => {
      setOpps(o);
      if (o[0]) setOppId(o[0].id);
    }).catch((e) => setError(e.message));
  }, []);

  async function generate() {
    setBusy(true);
    setError("");
    try {
      setResult(await api.generate(oppId, platform));
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }

  if (error && !opps.length) return <p className="error">API unavailable: {error}</p>;

  return (
    <>
      <h1>Create platform-ready content</h1>
      <div className="card">
        <label>Opportunity
          <select value={oppId} onChange={(e) => setOppId(Number(e.target.value))}>
            {opps.map((o) => (
              <option key={o.id} value={o.id}>{o.topic} ({o.score})</option>
            ))}
          </select>
        </label>
        <label>Platform
          <select value={platform} onChange={(e) => setPlatform(e.target.value)}>
            <option>LinkedIn</option>
            <option>X</option>
            <option>Blog</option>
          </select>
        </label>
        <p><button onClick={generate} disabled={busy || !oppId}>{busy ? "Working…" : "Generate"}</button></p>
        {error && <p className="error">{error}</p>}
      </div>
      {result && (
        <div className="card">
          <p><b>Quality {result.critique.overall}/10</b> — {result.critique.suggestion}</p>
          <pre style={{ whiteSpace: "pre-wrap" }}>{result.content.body}</pre>
        </div>
      )}
    </>
  );
}
