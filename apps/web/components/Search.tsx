"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { api } from "../lib/api";
import { Modal } from "./ui";

type Hit = { kind: string; title: string; sub: string; href: string };

export function useCommandK(open: () => void) {
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        open();
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open]);
}

export default function GlobalSearch({ open, onClose }: { open: boolean; onClose: () => void }) {
  const [q, setQ] = useState("");
  const [hits, setHits] = useState<Hit[]>([]);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    if (!open || q.trim().length < 2) {
      setHits([]);
      return;
    }
    setBusy(true);
    const id = setTimeout(() => {
      const needle = q.toLowerCase();
      Promise.all([
        api.trends(30).catch(() => []),
        api.opportunities().catch(() => []),
        api.library().catch(() => []),
        api.researchDocs(q, 10).catch(() => ({ documents: [] })),
      ]).then(([trends, opps, lib, res]) => {
        const out: Hit[] = [
          ...trends.filter((t) => t.topic.toLowerCase().includes(needle)).slice(0, 4)
            .map((t) => ({ kind: "Trend", title: t.topic, sub: `score ${t.trend_score}`, href: "/app/trends" })),
          ...opps.filter((o) => o.topic.toLowerCase().includes(needle)).slice(0, 4)
            .map((o) => ({ kind: "Opportunity", title: o.topic, sub: `score ${o.score}`, href: `/app/create?opp=${o.id}` })),
          ...lib.filter((c) => c.title.toLowerCase().includes(needle)).slice(0, 4)
            .map((c) => ({ kind: "Content", title: c.title.slice(0, 70), sub: c.platform, href: "/app/library" })),
          ...res.documents.slice(0, 4)
            .map((d) => ({ kind: "Research", title: d.title.slice(0, 70), sub: d.source, href: "/app/trends" })),
          { kind: "Action", title: `Ask agent about “${q}”`, sub: "agent", href: "/app/agent" },
        ];
        setHits(out);
        setBusy(false);
      });
    }, 220);
    return () => clearTimeout(id);
  }, [q, open]);

  return (
    <Modal open={open} onClose={onClose} title="Search">
      <input value={q} onChange={(e) => setQ(e.target.value)} placeholder="Content, trends, opportunities…"
        aria-label="Global search" autoFocus />
      {busy && <p className="muted">Searching…</p>}
      {!busy && q.trim().length >= 2 && !hits.length && <p className="muted">No matches.</p>}
      {hits.map((h, i) => (
        <p key={i}>
          <span className="pill">{h.kind}</span>{" "}
          <Link href={h.href} onClick={onClose}>{h.title}</Link>{" "}
          <span className="muted">· {h.sub}</span>
        </p>
      ))}
      <p className="muted">Ctrl/⌘ + K anywhere · Esc closes</p>
    </Modal>
  );
}
