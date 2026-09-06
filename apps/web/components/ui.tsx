"use client";

import { useCallback, useEffect, useState, type ReactNode } from "react";

export function Card({ children, glow = false }: { children: ReactNode; glow?: boolean }) {
  return <div className={"card" + (glow ? " glow" : "")}>{children}</div>;
}

export function Stat({ value, label, hot = false }: { value: string; label: string; hot?: boolean }) {
  return (
    <div className={"metric" + (hot ? " hot" : "")}>
      <b>{value}</b>
      <span>{label}</span>
    </div>
  );
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
