"use client";

import { Suspense, useEffect, useMemo, useState } from "react";
import { useSearchParams } from "next/navigation";
import { api, type Critique, type GenerateResult, type Opportunity } from "../../../lib/api";
import { toast } from "../../../components/fx";
import { Card, CopyButton, Empty, Pill, Quality, Tabs, Toggle, useApi } from "../../../components/ui";

const PLATS = ["LinkedIn", "X", "Blog", "Newsletter"];
const FORMATS = ["Insight + example + takeaway", "Tutorial", "Opinion", "Story", "News analysis"];

function words(s: string) {
  return s.split(/\s+/).filter(Boolean).length;
}

function readability(s: string): number {
  const w = words(s);
  if (!w) return 0;
  const sentences = Math.max(1, s.split(/[.!?\n]+/).filter((x) => x.trim()).length);
  const syllables = s.toLowerCase().split(/\s+/).filter(Boolean)
    .map((word) => Math.max(1, (word.match(/[aeiouy]+/g) ?? []).length)).reduce((a, b) => a + b, 0);
  return Math.max(0, Math.min(100, Math.round(206.835 - 1.015 * (w / sentences) - 84.6 * (syllables / w))));
}

type Draft = {
  brief: GenerateResult["brief"];
  critique: Critique;
  hook: string;
  title: string;
  body: string;
  savedId: number | null;
};

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
  const [drafts, setDrafts] = useState<Record<string, Draft>>({});
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [styleMatch, setStyleMatch] = useState(true);
  const [grounded, setGrounded] = useState(true);

  useEffect(() => {
    const q = Number(params.get("opp") ?? 0);
    if (q) setOppId(q);
    else if (opps.data?.[0] && !oppId) setOppId(opps.data[0].id);
    if (prefs.data && !tone) setTone(prefs.data.tone || "");
  }, [opps.data, oppId, params, prefs.data, tone]);

  const opp = (opps.data ?? []).find((o) => o.id === oppId);

  async function generate(plats: string[]) {
    setBusy(true);
    setError("");
    try {
      const out = { ...drafts };
      for (const p of plats) {
        const r = await api.generate(oppId, p, { tone: tone || undefined, length, style_match: styleMatch, grounded });
        out[p] = {
          brief: r.brief, critique: r.critique, hook: r.content.hook,
          title: r.content.title, body: r.content.body, savedId: null,
        };
        setDrafts({ ...out });
      }
      toast("Preview ready — nothing saved yet.");
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }

  async function improve(plat: string) {
    const d = drafts[plat];
    if (!d) return;
    setBusy(true);
    try {
      const r = await api.improvePreview(d.body, plat);
      setDrafts({ ...drafts, [plat]: { ...d, body: r.body, critique: r.critique } });
      toast(`Improved ${r.previous_score} → ${r.critique.overall}.`);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }

  async function save(plat: string) {
    const d = drafts[plat];
    if (!d) return;
    setBusy(true);
    try {
      const r = await api.save({
        opportunity_id: oppId, platform: plat, title: d.title,
        body: d.body, hook: d.hook, brief: d.brief as Record<string, unknown>,
      });
      setDrafts({ ...drafts, [plat]: { ...d, savedId: r.content.id } });
      toast("Saved to Library.");
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <>
      <h1>Create</h1>
      <p className="sub">Opportunity → voice → draft → critique → improve → preview → save.</p>
      <div className="workgrid">
        <div>
          <Card glow>
            {opp && (
              <>
                <p className="lbl">Selected opportunity</p>
                <p><b>{opp.topic}</b> — {opp.score}/100</p>
                <p className="muted">{opp.why_now}</p>
                <p className="muted">Angle: {opp.angle}</p>
              </>
            )}
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
              <Toggle checked={styleMatch} onChange={setStyleMatch} label="Match my best style" />
              <Toggle checked={grounded} onChange={setGrounded} label="Ground in research" />
            </div>
            <div className="row" style={{ marginTop: 10 }}>
              <button className="btn" onClick={() => generate([platform])} disabled={busy || !oppId}>
                {busy ? <><span className="spin" />Working…</> : "Generate"}
              </button>
              <button className="btn ghost" onClick={() => generate(PLATS)} disabled={busy || !oppId}>
                Generate all 3
              </button>
            </div>
            {error && <p className="error">Generation failed. No content was saved. ({error})</p>}
          </Card>
          {!opps.data?.length && !opps.busy && <Empty text="Generate opportunities first." />}
        </div>
        <Card>
          <h3>Session</h3>
          <p className="muted">{Object.keys(drafts).length} preview(s), {Object.values(drafts).filter((d) => d.savedId).length} saved.</p>
          <p className="muted">Previews live only here until you Save.</p>
        </Card>
      </div>
      {Object.entries(drafts).map(([plat, d]) => (
        <DraftCard key={plat} plat={plat} d={d} busy={busy} format={format}
          onBody={(body) => setDrafts({ ...drafts, [plat]: { ...d, body } })}
          onImprove={() => improve(plat)} onSave={() => save(plat)} />
      ))}
    </>
  );
}

function DraftCard({ plat, d, busy, format, onBody, onImprove, onSave }: {
  plat: string; d: Draft; busy: boolean; format: string;
  onBody: (b: string) => void; onImprove: () => void; onSave: () => void;
}) {
  const wc = words(d.body);
  const read = useMemo(() => readability(d.body), [d.body]);
  const fit = d.critique.scores.platform_fit ?? 0;
  return (
    <Card glow={!d.savedId}>
      <div className="row" style={{ alignItems: "center" }}>
        <Pill kind={plat}>{plat}</Pill>
        <Quality score={d.critique.overall} />
        {d.savedId ? <span className="pill good">Saved #{d.savedId}</span> : <span className="pill warn">Preview — not saved</span>}
        <span style={{ flex: 1 }} />
        <button className="btn ghost small" onClick={onImprove} disabled={busy}>Improve</button>
        {!d.savedId && <button className="btn small" onClick={onSave} disabled={busy}>Save</button>}
        <CopyButton text={d.body} />
      </div>
      <div className="dims">
        <span>{wc} words · {d.body.length} chars</span>
        <span>Readability {read}/100</span>
        <span>Platform fit {fit}/10</span>
        <span>Format: {format}</span>
      </div>
      <textarea value={d.body} onChange={(e) => onBody(e.target.value)} rows={12}
        aria-label={`${plat} draft editor`} style={{ marginTop: 10, fontSize: 14, lineHeight: 1.6 }} />
      <p className="muted">{d.critique.suggestion}</p>
      <details className="trace">
        <summary>Brief, evidence + score detail</summary>
        <pre className="draft">{JSON.stringify({
          angle: d.brief.angle, evidence: d.brief.supporting_evidence ?? [],
          style: ((d.brief.style_reference as string) || "").slice(0, 200) || "(none yet)",
          scores: d.critique.scores,
        }, null, 2)}</pre>
      </details>
    </Card>
  );
}
