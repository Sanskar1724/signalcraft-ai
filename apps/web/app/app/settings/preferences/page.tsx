"use client";

import Link from "next/link";
import { useState } from "react";
import { api, type Preferences } from "../../../../lib/api";
import { Card, Loading, useApi } from "../../../../components/ui";

const FORMATS = ["Tutorial", "Opinion", "Project breakdown", "News analysis",
  "Story", "Case study", "Educational", "Technical deep dive"];

export default function PreferencesPage() {
  const prefs = useApi(() => api.getPreferences());
  const [form, setForm] = useState<Partial<Preferences> | null>(null);
  const [saved, setSaved] = useState("");

  if (prefs.busy) return (<><h1>Preferences</h1><Loading /></>);
  if (prefs.error || !prefs.data) return (<><h1>Preferences</h1><div className="error">API unavailable: {prefs.error}</div></>);

  const cur = { ...prefs.data, ...(form ?? {}) };
  const set = (k: keyof Preferences, v: Preferences[keyof Preferences]) => setForm({ ...cur, [k]: v });

  async function save() {
    setSaved("");
    await api.savePreferences(form ?? {});
    setForm(null);
    prefs.reload();
    setSaved("Saved — generation and recommendations adapt immediately.");
  }

  return (
    <>
      <h1>Settings</h1>
      <div className="row" style={{ marginBottom: 4 }}>
        <Link href="/app/settings/profile" className="btn ghost small">Profile</Link>
        <Link href="/app/settings/preferences" className="btn small">Preferences</Link>
        <Link href="/app/settings/account" className="btn ghost small">Account</Link>
      </div>
      <h2>Content preferences</h2>
      <Card glow>
        <div className="grid3">
          <label className="field">Tone
            <select value={cur.tone} onChange={(e) => set("tone", e.target.value)}>
              {["", "Professional", "Technical", "Conversational", "Opinionated", "Simple"].map((t) => (
                <option key={t} value={t}>{t || "— profile default —"}</option>
              ))}
            </select>
          </label>
          <label className="field">Length
            <select value={cur.length} onChange={(e) => set("length", e.target.value)}>
              {["short", "medium", "long"].map((t) => <option key={t}>{t}</option>)}
            </select>
          </label>
          <label className="field">Creativity ({cur.creativity})
            <input type="range" min={0} max={1} step={0.1} value={cur.creativity}
              onChange={(e) => set("creativity", Number(e.target.value))} />
          </label>
          <label className="field">Research depth
            <select value={cur.research_depth} onChange={(e) => set("research_depth", e.target.value)}>
              {["quick", "standard", "deep"].map((t) => <option key={t}>{t}</option>)}
            </select>
          </label>
          <label className="field">Formality
            <select value={cur.formality} onChange={(e) => set("formality", e.target.value)}>
              {["casual", "neutral", "formal"].map((t) => <option key={t}>{t}</option>)}
            </select>
          </label>
          <label className="field">Emoji preference
            <select value={cur.emoji_pref} onChange={(e) => set("emoji_pref", e.target.value)}>
              {["none", "minimal", "free"].map((t) => <option key={t}>{t}</option>)}
            </select>
          </label>
          <label className="field">CTA preference
            <select value={cur.cta_pref} onChange={(e) => set("cta_pref", e.target.value)}>
              {["question", "link", "follow", "none"].map((t) => <option key={t}>{t}</option>)}
            </select>
          </label>
          <label className="field">Citation preference
            <select value={cur.citation_pref} onChange={(e) => set("citation_pref", e.target.value)}>
              {["link", "footnote", "none"].map((t) => <option key={t}>{t}</option>)}
            </select>
          </label>
          <label className="field">Posting frequency
            <select value={cur.frequency} onChange={(e) => set("frequency", e.target.value)}>
              {["1–2 / week", "3–5 / week", "Daily", "Flexible"].map((t) => <option key={t}>{t}</option>)}
            </select>
          </label>
        </div>
        <p className="lbl">Formats</p>
        <div className="chips">
          {FORMATS.map((o) => (
            <button key={o} type="button" className={"chip" + (cur.formats.includes(o) ? " on" : "")}
              onClick={() => set("formats", cur.formats.includes(o) ? cur.formats.filter((x) => x !== o) : [...cur.formats, o])}>
              {o}
            </button>
          ))}
        </div>
        <h2>AI behavior</h2>
        <div className="row">
          <label className="field" style={{ flexDirection: "row", alignItems: "center", gap: 8 }}>
            <input type="checkbox" style={{ width: 18 }} checked={!!cur.use_trends}
              onChange={(e) => set("use_trends", e.target.checked ? 1 : 0)} /> Use current trends
          </label>
          <label className="field" style={{ flexDirection: "row", alignItems: "center", gap: 8 }}>
            <input type="checkbox" style={{ width: 18 }} checked={!!cur.always_research}
              onChange={(e) => set("always_research", e.target.checked ? 1 : 0)} /> Always research before generation
          </label>
        </div>
        <p style={{ marginBottom: 0 }}>
          <button className="btn" onClick={save} disabled={!form}>Save preferences</button>
        </p>
        {saved && <p className="muted">{saved}</p>}
      </Card>
    </>
  );
}
