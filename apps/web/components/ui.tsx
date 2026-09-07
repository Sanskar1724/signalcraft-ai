"use client";

import { useCallback, useEffect, useState, type ReactNode } from "react";
export function Card({ children, glow = false, lift = false }: { children: ReactNode; glow?: boolean; lift?: boolean }) {
  return <div className={"card" + (glow ? " glow" : "") + (lift ? " lift" : "")}>{children}</div>;
}

export function Stat({ value, label, hot = false }: { value: string; label: string; hot?: boolean }) {
  return (
    <div className="metric" style={{ transition: "transform .18s ease, border-color .18s ease" }}
      onMouseEnter={(e) => { e.currentTarget.style.transform = "translateY(-2px)"; }}
      onMouseLeave={(e) => { e.currentTarget.style.transform = "none"; }}>
      <b><CountUp text={value} /></b>
      <span>{label}</span>
    </div>
  );
}

export function CountUp({ text }: { text: string }) {
  const m = text.match(/^(-?[\d.]+)(.*)$/);
  const [n, setN] = useState(text);
  useEffect(() => {
    if (!m) {
      setN(text);
      return;
    }
    const target = parseFloat(m[1]);
    const suffix = m[2];
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches || !Number.isFinite(target)) {
      setN(text);
      return;
    }
    let raf = 0;
    const t0 = performance.now();
    const step = (t: number) => {
      const p = Math.min(1, (t - t0) / 900);
      const eased = 1 - Math.pow(1 - p, 3);
      const cur = target * eased;
      setN((target % 1 === 0 ? String(Math.round(cur)) : cur.toFixed(1)) + suffix);
      if (p < 1) raf = requestAnimationFrame(step);
    };
    raf = requestAnimationFrame(step);
    return () => cancelAnimationFrame(raf);
  }, [text]);
  return <>{n}</>;
}

export function ScoreBar({ value, max = 100 }: { value: number; max?: number }) {
  return (
    <div className="bar">
      <i style={{ width: `${Math.max(0, Math.min(100, (value / max) * 100))}%` }} />
    </div>
  );
}

export function Pill({ kind, children }: { kind?: string; children: ReactNode }) {
  const cls = kind === "LinkedIn" ? "pill li" : kind === "X" ? "pill x" : kind === "Blog" ? "pill blog" : "pill";
  return <span className={cls}>{children}</span>;
}

export function Quality({ score }: { score: number }) {
  const kind = score >= 8 ? "good" : score >= 6 ? "warn" : "";
  return (
    <span className={"pill " + kind} style={{ margin: 0 }}>
      Q {score}/10
    </span>
  );
}

export function Loading() {
  return (
    <>
      <div className="sk" />
      <div className="sk" />
      <div className="sk" />
    </>
  );
}

export function Empty({ text }: { text: string }) {
  return (
    <div className="card">
      <p className="muted" style={{ margin: 0 }}>{text}</p>
    </div>
  );
}

export function CopyButton({ text }: { text: string }) {
  const [done, setDone] = useState(false);
  return (
    <button
      className="btn ghost small"
      onClick={async () => {
        await navigator.clipboard.writeText(text);
        setDone(true);
        setTimeout(() => setDone(false), 1500);
      }}
    >
      {done ? "Copied" : "Copy"}
    </button>
  );
}

export function useApi<T>(fn: () => Promise<T>, deps: unknown[] = []) {
  const [data, setData] = useState<T | null>(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(true);
  const load = useCallback(() => {
    setBusy(true);
    setError("");
    fn()
      .then(setData)
      .catch((e) => setError(e.message))
      .finally(() => setBusy(false));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps);
  useEffect(load, [load]);
  return { data, error, busy, reload: load };
}

export function Modal({ open, onClose, title, children }: { open: boolean; onClose: () => void; title: string; children: ReactNode }) {
  if (!open) return null;
  return (
    <div className="overlay" onClick={onClose}>
      <div className="sheet" onClick={(e) => e.stopPropagation()}>
        <div className="row" style={{ alignItems: "center" }}>
          <h3 style={{ margin: 0, flex: 1 }}>{title}</h3>
          <button className="btn ghost small" onClick={onClose}>Close</button>
        </div>
        {children}
      </div>
    </div>
  );
}

export function Tabs({ tabs, active, onChange }: { tabs: string[]; active: string; onChange: (t: string) => void }) {
  return (
    <div className="row" style={{ gap: 6 }}>
      {tabs.map((t) => (
        <button key={t} className={t === active ? "btn small" : "btn ghost small"} onClick={() => onChange(t)}>
          {t}
        </button>
      ))}
    </div>
  );
}

export function ApiStatus({ check }: { check: () => Promise<unknown> }) {
  const [ok, setOk] = useState<boolean | null>(null);
  useEffect(() => {
    let live = true;
    const ping = () => check().then(() => live && setOk(true)).catch(() => live && setOk(false));
    ping();
    const id = setInterval(ping, 30000);
    return () => { live = false; clearInterval(id); };
  }, [check]);
  return (
    <span className="statuspill" title={ok === null ? "checking" : ok ? "API live" : "API unreachable"}>
      <span className={"livedot" + (ok === true ? " on" : ok === false ? " off" : "")} />
      {ok === null ? "connecting" : ok ? "live" : "offline"}
    </span>
  );
}
