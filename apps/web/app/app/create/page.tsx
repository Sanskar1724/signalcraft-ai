"use client";

import { Suspense, useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import { api, type GenerateResult, type Opportunity } from "../../../lib/api";
import { toast } from "../../../components/fx";
import { Card, CopyButton, Empty, Pill, Quality, Tabs, useApi } from "../../../components/ui";

const PLATS = ["LinkedIn", "X", "Blog"];
const FORMATS = ["Insight + example + takeaway", "Tutorial", "Opinion", "Story", "News analysis"];

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
  const prefs = useApi(() => api.getPreferences());
  const params = useSearchParams();
  const [oppId, setOppId] = useState(0);
  const [platform, setPlatform] = useState("LinkedIn");
  const [tone, setTone] = useState("");
  const [format, setFormat] = useState(FORMATS[0]);
  const [length, setLength] = useState("medium");
  const [results, setResults] = useState<Record<string, GenerateResult & { id: number }>>({});
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    const q = Number(params.get("opp") ?? 0);
    if (q) setOppId(q);
    else if (opps.data?.[0] && !oppId) setOppId(opps.data[0].id);
    if (prefs.data && !tone) setTone(prefs.data.tone || "");
  }, [opps.data, oppId, params, prefs.data, tone]);

  async function generate(plats: string[]) {
    setBusy(true);
    setError("");
    try {
      const out: Record<string, GenerateResult & { id: number }> = { ...results };
      for (const p of plats) {
        const r = await api.generate(oppId, p, { tone: tone || undefined, length });
        out[p] = { ...r, id: r.content.id };
        setResults({ ...out });
      }
      toast("Draft generated — brief, critique and validation attached.");
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }

  async function improve(plat: string) {
    const cur = results[plat];
    if (!cur) return;
    setBusy(true);
    try {
      const r = await api.revise(cur.id);
      setResults({ ...results, [plat]: { ...cur, content: { ...cur.content, body: r.body }, critique: r.critique } });
      toast("Improved — saved as a new version.");
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }

  async function saveReady(plat: string) {
    const cur = results[plat];
    if (!cur) return;
    await api.setStatus(cur.id, "ready");
    toast("Marked ready — find it in Library.");
  }

  return (
    <>
      <h1>Create</h1>
      <p className="sub">Workspace: opportunity, voice, format — then generate, critique, improve, save.</p>
      <div className="workgrid">
        <div>
          <Card glow>
            <label className="field">Opportunity
              <select value={oppId} onChange={(e) => setOppId(Number(e.target.value))}>
                {(opps.data ?? []).map((o: Opportunity) => (
                  <option key={o.id} value={o.id}>{o.topic} ({o.score})</option>
                ))}
              </select>
            </label>
            <div className="grid3" style={{ marginTop: 10 }}>
              <label className="field">Tone override
                <select value={tone} onChange={(e) => setTone(e.target.value)}>
                  <option value="">— preference default —</option>
                  {["Professional", "Technical", "Conversational", "Opinionated", "Simple"].map((t) => (
                    <option key={t}>{t}</option>
                  ))}
                </select>
              </label>
              <label className="field">Format
                <select value={format} onChange={(e) => setFormat(e.target.value)}>
                  {FORMATS.map((t) => <option key={t}>{t}</option>)}
                </select>
              </label>
              <label className="field">Length
                <select value={length} onChange={(e) => setLength(e.target.value)}>
                  <option value="short">Short</option>
                  <option value="medium">Medium</option>
                  <option value="long">Long</option>
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
        </div>
        <Card>
          <h3>Content score</h3>
          {Object.entries(results).map(([plat, r]) => (
            <div key={plat} style={{ marginBottom: 10 }}>
              <p className="muted" style={{ margin: "4px 0" }}>{plat} — <b style={{ color: "var(--text)" }}>{r.critique.overall}/10</b></p>
              {Object.entries(r.critique.scores).slice(0, 5).map(([k, v]) => (
                <p key={k} className="muted" style={{ margin: "2px 0", fontSize: 12 }}>{k}: {v}</p>
              ))}
            </div>
          ))}
          {!Object.keys(results).length && <p className="muted">Scores appear here after generation.</p>}
        </Card>
      </div>
      {Object.entries(results).map(([plat, r]) => (
        <Card key={plat}>
          <div className="row" style={{ alignItems: "center" }}>
            <Pill kind={plat}>{plat}</Pill>
            <Quality score={r.critique.overall} />
            <span className="muted">{words(r.content.body)} words · {r.content.body.length} chars · {format}</span>
            <span style={{ flex: 1 }} />
            <button className="btn ghost small" onClick={() => improve(plat)} disabled={busy}>Improve</button>
            <button className="btn ghost small" onClick={() => saveReady(plat)}>Save</button>
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
