"use client";

import Link from "next/link";
import { useState } from "react";
import { api, type Profile } from "../../../../lib/api";
import { Card, Loading, useApi } from "../../../../components/ui";

const FIELDS: [keyof Profile, string][] = [
  ["name", "Name"],
  ["role", "Professional role"],
  ["bio", "Short bio"],
  ["location", "Location / timezone"],
  ["niche", "Niche"],
  ["expertise", "Expertise"],
  ["expertise_level", "Expertise level"],
  ["audience", "Audience"],
  ["goals", "Goals"],
  ["writing_style", "Writing style"],
  ["tone", "Tone"],
  ["content_preferences", "Content preferences"],
  ["posting_preferences", "Posting preferences"],
  ["style_notes", "Style notes"],
];

function SubNav() {
  return (
    <div className="row" style={{ marginBottom: 4 }}>
      <Link href="/app/settings/profile" className="btn small">Profile</Link>
      <Link href="/app/settings/preferences" className="btn ghost small">Preferences</Link>
      <Link href="/app/settings/account" className="btn ghost small">Account</Link>
    </div>
  );
}

export default function ProfileSettingsPage() {
  const prof = useApi(() => api.profile());
  const [form, setForm] = useState<Partial<Profile> | null>(null);
  const [saved, setSaved] = useState("");

  if (prof.busy) return (<><h1>Profile</h1><Loading /></>);
  if (prof.error || !prof.data) return (<><h1>Profile</h1><div className="error">API unavailable: {prof.error}</div></>);

  const cur = { ...prof.data, ...(form ?? {}) };

  async function save() {
    setSaved("");
    await api.updateProfile(form ?? {});
    setForm(null);
    prof.reload();
    setSaved("Saved — recommendations now use this.");
  }

  return (
    <>
      <h1>Settings</h1>
      <SubNav />
      <h2>Profile</h2>
      <Card glow>
        <label className="field">Preferred topics (comma separated)
          <input
            value={(cur.topics ?? []).join(", ")}
            onChange={(e) => setForm({ ...cur, topics: e.target.value.split(",").map((t) => t.trim()).filter(Boolean) })}
          />
        </label>
        <label className="field" style={{ marginTop: 10 }}>Topics to avoid
          <input
            value={(cur.avoid_topics ?? []).join(", ")}
            onChange={(e) => setForm({ ...cur, avoid_topics: e.target.value.split(",").map((t) => t.trim()).filter(Boolean) })}
          />
        </label>
        <div className="grid3" style={{ marginTop: 10 }}>
          {FIELDS.map(([k, label]) => (
            <label className="field" key={k} style={{ minWidth: 160 }}>{label}
              <input value={(cur[k] as string) ?? ""} onChange={(e) => setForm({ ...cur, [k]: e.target.value })} />
            </label>
          ))}
        </div>
        <p style={{ marginBottom: 0 }}>
          <button className="btn" onClick={save} disabled={!form}>Save profile</button>
        </p>
        {saved && <p className="muted">{saved}</p>}
      </Card>
    </>
  );
}
