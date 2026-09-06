"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import Logo from "../../components/Logo";
import SignalField from "../../components/SignalField";
import { api } from "../../lib/api";
import { getToken } from "../../lib/auth";

const GOALS = ["Personal branding", "Grow audience", "Build authority", "Get job opportunities",
  "Generate leads", "Promote projects", "Share knowledge", "Build community"];
const STYLES = ["Professional", "Technical", "Educational", "Conversational",
  "Opinionated", "Storytelling", "Simple", "Analytical"];
const FORMATS = ["Tutorial", "Opinion", "Project breakdown", "News analysis",
  "Story", "Case study", "Educational", "Technical deep dive"];
const FREQS = ["1–2 / week", "3–5 / week", "Daily", "Flexible"];
const PLATFORMS = ["LinkedIn", "X", "Blog", "Newsletter"];

const META = [
  ["You & your expertise", "Who you are and what you know. This focuses all research on your world."],
  ["Audience & goals", "Who you create for and what winning looks like. Every recommendation is scored against this."],
  ["Voice & rhythm", "How you sound, what you cover, where you publish. Generation follows this exactly."],
];

function Chips({ options, value, onChange, multi = true }: {
  options: string[]; value: string[]; onChange: (v: string[]) => void; multi?: boolean;
}) {
  function toggle(o: string) {
    onChange(multi
      ? (value.includes(o) ? value.filter((x) => x !== o) : [...value, o])
      : [o]);
  }
  return (
    <div className="chips">
      {options.map((o) => (
        <button key={o} type="button" className={"chip" + (value.includes(o) ? " on" : "")} onClick={() => toggle(o)}>
          {o}
        </button>
      ))}
    </div>
  );
}

const csv = (s: string) => s.split(",").map((t) => t.trim()).filter(Boolean);

export default function OnboardingPage() {
  const router = useRouter();
  const [step, setStep] = useState(0);
  const [busy, setBusy] = useState(false);
  const [building, setBuilding] = useState(false);
  const [error, setError] = useState("");
  const [done, setDone] = useState<Record<string, unknown> | null>(null);
  const [f, setF] = useState<Record<string, string | string[]>>({
    name: "", role: "", bio: "", location: "", niche: "", secondary_topics: [],
    expertise_level: "", audience: "", audience_segments: [], goals: [],
    writing_style: "", tone: "", style_notes: "", topics: [], avoid_topics: [],
    formats: [], frequency: "", platforms: ["LinkedIn", "X", "Blog"],
  });
  const set = (k: string, v: string | string[]) => setF({ ...f, [k]: v });

  if (typeof window !== "undefined" && !getToken()) {
    router.replace("/login");
    return <p className="muted">Redirecting…</p>;
  }

  async function save(patch: Record<string, unknown>) {
    setError("");
    try {
      await api.onboardStep(patch);
    } catch (e) {
      setError((e as Error).message);
      throw e;
    }
  }

  function collect(s: number): Record<string, unknown> {
    if (s === 0) {
      return { name: f.name, role: f.role, bio: f.bio, location: f.location,
               niche: f.niche, secondary_topics: f.secondary_topics,
               expertise_level: f.expertise_level };
    }
    if (s === 1) {
      return { audience: f.audience, audience_segments: f.audience_segments, goals: f.goals };
    }
    return { writing_style: f.writing_style, tone: f.tone, style_notes: f.style_notes,
             topics: f.topics, avoid_topics: f.avoid_topics, formats: f.formats,
             frequency: f.frequency, platforms: f.platforms };
  }

  async function next() {
    setBusy(true);
    try {
      await save(collect(step));
      setStep(step + 1);
    } catch { /* error shown */ } finally {
      setBusy(false);
    }
  }

  async function finish() {
    setBusy(true);
    setBuilding(true);
    try {
      await save(collect(2));
      const r = await api.onboardComplete();
      setDone(r.summary);
    } catch { /* shown */ } finally {
      setBusy(false);
    }
  }

  if (done) {
    const d = done as Record<string, string | string[]>;
    return (
      <div className="wizwrap">
        <p className="kicker">Setup complete</p>
        <h1>Your content profile</h1>
        <div className="card glow">
          {Object.entries({ Niche: d.niche, Audience: d.audience, Goals: d.goals, Style: d.style, Platforms: d.platforms }).map(([k, v]) => (
            <p key={k}><span className="muted">{k}:</span> <b>{Array.isArray(v) ? v.join(" + ") : v}</b></p>
          ))}
        </div>
        <p><button className="btn" onClick={() => router.replace("/app")}>Build my content intelligence</button></p>
      </div>
    );
  }

  const [title, explain] = META[step];

  return (
    <div className="wiz">
      <SignalField />
      <aside className="wizside">
        <p><Logo size={32} /></p>
        <p className="kicker">Welcome to SignalCraft</p>
        <h2 className="landh" style={{ fontSize: 26 }}>Step {step + 1} — {title}</h2>
        <p className="muted">{explain}</p>
        <div className="steps">{META.map((_, i) => <i key={i} className={i <= step ? "on" : ""} />)}</div>
        <p className="muted">Progress saves automatically as you continue.</p>
      </aside>
      <div>
        <div className="card">
          {step === 0 && (
            <>
              <div className="grid2">
                <label className="field">Your name
                  <input value={f.name as string} onChange={(e) => set("name", e.target.value)} placeholder="Sankiyy" autoComplete="name" /></label>
                <label className="field">What do you do?
                  <input value={f.role as string} onChange={(e) => set("role", e.target.value)} placeholder="AI / Data Engineering" /></label>
              </div>
              <label className="field" style={{ marginTop: 10 }}>Short introduction
                <input value={f.bio as string} onChange={(e) => set("bio", e.target.value)} placeholder="Building AI and data engineering projects…" /></label>
              <div className="grid2" style={{ marginTop: 10 }}>
                <label className="field">Primary niche
                  <input value={f.niche as string} onChange={(e) => set("niche", e.target.value)} placeholder="AI + Data Engineering" /></label>
                <label className="field">Location / timezone (optional)
                  <input value={f.location as string} onChange={(e) => set("location", e.target.value)} placeholder="IST" /></label>
              </div>
              <label className="field" style={{ marginTop: 10 }}>Secondary topics (comma separated)
                <input value={(f.secondary_topics as string[]).join(", ")} onChange={(e) => set("secondary_topics", csv(e.target.value))} placeholder="LLMs, AI Agents, PySpark" /></label>
              <p className="lbl">Expertise level</p>
              <Chips options={["Beginner", "Intermediate", "Advanced", "Expert"]} value={[f.expertise_level as string]} onChange={([v]) => set("expertise_level", v ?? "")} multi={false} />
            </>
          )}

          {step === 1 && (
            <>
              <label className="field">Who are you creating for? (one line)
                <input value={f.audience as string} onChange={(e) => set("audience", e.target.value)} placeholder="Developers, Data Engineers, Students" /></label>
              <p className="lbl">Audience segments</p>
              <Chips options={["Developers", "Data Engineers", "Students", "Founders", "Designers", "Managers"]}
                value={f.audience_segments as string[]} onChange={(v) => set("audience_segments", v)} />
              <p className="lbl">Goals — pick all that apply</p>
              <Chips options={GOALS} value={f.goals as string[]} onChange={(v) => set("goals", v)} />
              <label className="field" style={{ marginTop: 10 }}>Custom goal (optional)
                <input placeholder="e.g. Document my learning" onBlur={(e) => {
                  const v = e.target.value.trim();
                  if (v && !(f.goals as string[]).includes(v)) set("goals", [...(f.goals as string[]), v]);
                }} /></label>
            </>
          )}

          {step === 2 && (
            <>
              <p className="lbl">How do you want to sound?</p>
              <Chips options={STYLES} value={(f.writing_style as string).split(" + ").filter(Boolean)}
                onChange={(v) => set("writing_style", v.join(" + "))} />
              <div className="grid2" style={{ marginTop: 10 }}>
                <label className="field">Tone
                  <input value={f.tone as string} onChange={(e) => set("tone", e.target.value)} placeholder="Technical + simple" /></label>
                <label className="field">Posting frequency
                  <input value={f.frequency as string} onChange={(e) => set("frequency", e.target.value)} placeholder="3–5 / week" /></label>
              </div>
              <label className="field" style={{ marginTop: 10 }}>Describe your style
                <input value={f.style_notes as string} onChange={(e) => set("style_notes", e.target.value)}
                  placeholder="Technical but simple. No AI hype." /></label>
              <div className="grid2" style={{ marginTop: 10 }}>
                <label className="field">Topics to cover
                  <input value={(f.topics as string[]).join(", ")} onChange={(e) => set("topics", csv(e.target.value))} placeholder="AI agents, LLMs" /></label>
                <label className="field">Topics to avoid
                  <input value={(f.avoid_topics as string[]).join(", ")} onChange={(e) => set("avoid_topics", csv(e.target.value))} placeholder="Hype, clickbait" /></label>
              </div>
              <p className="lbl">Formats</p>
              <Chips options={FORMATS} value={f.formats as string[]} onChange={(v) => set("formats", v)} />
              <p className="lbl">Platforms</p>
              <Chips options={PLATFORMS} value={f.platforms as string[]} onChange={(v) => set("platforms", v)} />
            </>
          )}

          {error && <p className="error">{error}</p>}
          <div className="row" style={{ marginTop: 14 }}>
            {step > 0 && <button className="btn ghost" onClick={() => setStep(step - 1)} disabled={busy}>Back</button>}
            <span style={{ flex: 1 }} />
            {step < 2 ? (
              <button className="btn" onClick={() => next()} disabled={busy || (step === 0 && (!(f.name as string).trim() || !(f.niche as string).trim()))}>
                {busy ? "Saving…" : "Continue →"}
              </button>
            ) : (
              <button className="btn" onClick={finish} disabled={busy}>
                {building ? <><span className="spin" />Building your intelligence…</> : "Complete setup"}
              </button>
            )}
          </div>
          {building && <p className="muted">Researching your niche and ranking your first opportunities.</p>}
        </div>
      </div>
    </div>
  );
}
