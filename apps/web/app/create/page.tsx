"use client";

import { Suspense, useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import { api, type GenerateResult, type Opportunity } from "../../lib/api";
import { Card, CopyButton, Empty, Pill, Quality, Tabs, useApi } from "../../components/ui";

const PLATS = ["LinkedIn", "X", "Blog"];

function words(s: string) {
  return s.split(/\s+/).filter(Boolean).length;
}

export default function CreatePage() {
  return (
    <Suspense>
      <CreateInner />
    </Suspense>
  );
}

function CreateInner() {
  const opps = useApi(() => api.opportunities());
  const params = useSearchParams();
  const [oppId, setOppId] = useState(0);
  const [platform, setPlatform] = useState("LinkedIn");
  const [results, setResults] = useState<Record<string, GenerateResult>>({});
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    const q = Number(params.get("opp") ?? 0);
    if (q) setOppId(q);
    else if (opps.data?.[0] && !oppId) setOppId(opps.data[0].id);
  }, [opps.data, oppId, params]);

  async function generate(plats: string[]) {
    setBusy(true);
    setError("");
    try {
      const out: Record<string, GenerateResult> = {};
      for (const p of plats) {
        out[p] = await api.generate(oppId, p);
        setResults({ ...out });
      }
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <>
      <h1>Create</h1>
      <p className="sub">Brief → draft → critique → validate. One platform or all three.</p>
      <Card glow>
        <div className="row">
          <label className="field">Opportunity
            <select value={oppId} onChange={(e) => setOppId(Number(e.target.value))}>
              {(opps.data ?? []).map((o: Opportunity) => (
                <option key={o.id} value={o.id}>{o.topic} ({o.score})</option>
              ))}
            </select>
          </label>
        </div>
        <div style={{ margin: "10px 0" }}>
          <Tabs tabs={PLATS} active={platform} onChange={setPlatform} />
        </div>
        <div className="row">
          <button className="btn" onClick={() => generate([platform])} disabled={busy || !oppId}>
            {busy ? <><span className="spin" />Working…</> : "Generate"}
          </button>
          <button className="btn ghost" onClick={() => generate(PLATS)} disabled={busy || !oppId}>
            Generate all 3 platforms
          </button>
        </div>
        {error && <p className="error">{error}</p>}
      </Card>
      {!opps.data?.length && !opps.busy && <Empty text="Generate opportunities first." />}
      {Object.entries(results).map(([plat, r]) => (
        <Card key={plat}>
          <div className="row" style={{ alignItems: "center" }}>
            <Pill kind={plat}>{plat}</Pill>
            <Quality score={r.critique.overall} />
            <span className="muted">{words(r.content.body)} words · {r.content.body.length} chars</span>
            <span style={{ flex: 1 }} />
            <CopyButton text={r.content.body} />
          </div>
          <p className="muted">{r.critique.suggestion}</p>
          <pre className="draft">{r.content.body}</pre>
          <details className="trace">
            <summary>Content brief + critique detail</summary>
            <pre className="draft">{JSON.stringify({ brief: r.brief, scores: r.critique.scores }, null, 2)}</pre>
          </details>
        </Card>
      ))}
    </>
  );
}
