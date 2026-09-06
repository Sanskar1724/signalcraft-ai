"use client";

import { useEffect, useState } from "react";
import { api, type GenerateResult, type Opportunity } from "../../lib/api";
import { Card, CopyButton, Empty, Pill, Quality, useApi } from "../../components/ui";

export default function CreatePage() {
  const opps = useApi(() => api.opportunities());
  const [oppId, setOppId] = useState(0);
  const [platform, setPlatform] = useState("LinkedIn");
  const [result, setResult] = useState<GenerateResult | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (opps.data?.[0] && !oppId) setOppId(opps.data[0].id);
  }, [opps.data, oppId]);

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

  return (
    <>
      <h1>Create</h1>
      <p className="sub">Brief → draft → critique → validate. Regenerate anytime.</p>
      <Card glow>
        <div className="row">
          <label className="field">Opportunity
            <select value={oppId} onChange={(e) => setOppId(Number(e.target.value))}>
              {(opps.data ?? []).map((o: Opportunity) => (
                <option key={o.id} value={o.id}>{o.topic} ({o.score})</option>
              ))}
            </select>
          </label>
          <label className="field" style={{ minWidth: 140, flex: 0 }}>Platform
            <select value={platform} onChange={(e) => setPlatform(e.target.value)}>
              <option>LinkedIn</option>
              <option>X</option>
              <option>Blog</option>
            </select>
          </label>
        </div>
        <p style={{ marginBottom: 0 }}>
          <button className="btn" onClick={generate} disabled={busy || !oppId}>
            {busy ? <><span className="spin" />Working…</> : result ? "Regenerate" : "Generate"}
          </button>
        </p>
        {error && <p className="error">{error}</p>}
      </Card>
      {!opps.data?.length && !opps.busy && <Empty text="Generate opportunities first." />}
      {result && (
        <Card>
          <div className="row" style={{ alignItems: "center" }}>
            <Quality score={result.critique.overall} />
            <span className="muted">{result.critique.suggestion}</span>
            <span style={{ flex: 1 }} />
            <Pill kind={platform}>{platform}</Pill>
            <CopyButton text={result.content.body} />
          </div>
          <pre className="draft">{result.content.body}</pre>
          <details className="trace">
            <summary>Content brief + critique detail</summary>
            <pre className="draft">{JSON.stringify({ brief: result.brief, scores: result.critique.scores }, null, 2)}</pre>
          </details>
        </Card>
      )}
    </>
  );
}
