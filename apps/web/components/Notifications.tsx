"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { api } from "../lib/api";

type Note = { key: string; text: string; href: string };

function compute(): Promise<Note[]> {
  return Promise.all([
    api.opportunities().catch(() => []),
    api.calendar().catch(() => ({ items: [] })),
    api.library().catch(() => []),
  ]).then(([opps, cal, lib]) => {
    const out: Note[] = [];
    for (const o of opps.filter((x) => x.score >= 85).slice(0, 3)) {
      out.push({ key: `opp-${o.id}`, text: `High-score opportunity: ${o.topic} (${o.score})`, href: "/app/opportunities" });
    }
    const soon = Date.now() + 48 * 3600 * 1000;
    for (const e of cal.items.filter((x) => x.status !== "published")) {
      const t = new Date(e.scheduled_for.replace(" ", "T") + "Z").getTime();
      if (!Number.isNaN(t) && t > Date.now() && t < soon) {
        out.push({ key: `cal-${e.scheduled_for}-${e.platform}`, text: `Due soon: [${e.platform}] ${e.title ?? e.notes}`, href: "/app/calendar" });
      }
    }
    for (const c of lib.filter((x) => x.quality_score > 0 && x.quality_score < 7.5).slice(0, 3)) {
      out.push({ key: `low-${c.id}`, text: `Needs improvement: ${c.title.slice(0, 60)}`, href: "/app/library" });
    }
    return out;
  }).catch(() => []);
}

export default function Notifications() {
  const [notes, setNotes] = useState<Note[]>([]);
  const [open, setOpen] = useState(false);
  const [seen, setSeen] = useState<Set<string>>(new Set());

  useEffect(() => {
    compute().then(setNotes);
    const id = setInterval(() => compute().then(setNotes), 120000);
    return () => clearInterval(id);
  }, []);

  const fresh = notes.filter((n) => !seen.has(n.key));

  return (
    <div style={{ position: "relative" }}>
      <button className="iconbtn" aria-label={`Notifications (${fresh.length} unread)`}
        onClick={() => { setOpen(!open); setNotes((ns) => { setSeen(new Set(ns.map((n) => n.key))); return ns; }); }}>
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden>
          <path d="M18 8a6 6 0 0 0-12 0c0 7-3 9-3 9h18s-3-2-3-9" />
          <path d="M13.7 21a2 2 0 0 1-3.4 0" />
        </svg>
        {fresh.length > 0 && ` ${fresh.length}`}
      </button>
      {open && (
        <div className="menu" role="menu" aria-label="Notifications">
          {fresh.length === 0 && <p className="muted" style={{ padding: "6px 12px" }}>All caught up.</p>}
          {fresh.map((n) => (
            <Link key={n.key} href={n.href} onClick={() => setOpen(false)}>{n.text}</Link>
          ))}
        </div>
      )}
    </div>
  );
}
