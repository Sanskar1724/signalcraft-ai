"use client";

import { useState } from "react";
import { api, type CalendarItem } from "../../../lib/api";
import { Card, Empty, Loading, Pill, useApi } from "../../../components/ui";

function monthCells(year: number, month: number, items: CalendarItem[]) {
  const first = new Date(year, month, 1);
  const startDay = (first.getDay() + 6) % 7; // Monday-first
  const days = new Date(year, month + 1, 0).getDate();
  const cells: { day: number | null; evs: CalendarItem[] }[] = [];
  for (let i = 0; i < startDay; i++) cells.push({ day: null, evs: [] });
  for (let d = 1; d <= days; d++) {
    const key = `${year}-${String(month + 1).padStart(2, "0")}-${String(d).padStart(2, "0")}`;
    cells.push({ day: d, evs: items.filter((e) => e.scheduled_for.slice(0, 10) === key) });
  }
  return cells;
}

const MONTHS = ["January", "February", "March", "April", "May", "June",
  "July", "August", "September", "October", "November", "December"];

export default function CalendarPage() {
  const cal = useApi(() => api.calendar());
  const now = new Date();
  const [ym, setYm] = useState<[number, number]>([now.getFullYear(), now.getMonth()]);
  const [platform, setPlatform] = useState("LinkedIn");
  const [when, setWhen] = useState("2026-09-10T10:00");
  const [notes, setNotes] = useState("");
  const [saved, setSaved] = useState("");

  async function schedule() {
    setSaved("");
    await api.schedule({ platform, scheduled_for: when.replace("T", " "), notes });
    setSaved("Scheduled.");
    cal.reload();
  }

  if (cal.busy) return (<><h1>Content Calendar</h1><Loading /></>);
  if (cal.error || !cal.data) return (<><h1>Content Calendar</h1><div className="error">API unavailable: {cal.error}</div></>);

  const [year, month] = ym;
  const cells = monthCells(year, month, cal.data.items);
  const shift = (d: number) => {
    const dt = new Date(year, month + d, 1);
    setYm([dt.getFullYear(), dt.getMonth()]);
  };

  return (
    <>
      <h1>Content Calendar</h1>
      <p className="sub">Plan what ships, where, and when. Scheduling is real; publishing stays manual (§58).</p>
      <Card glow>
        <div className="row">
          <label className="field" style={{ minWidth: 140, flex: 0 }}>Platform
            <select value={platform} onChange={(e) => setPlatform(e.target.value)}>
              <option>LinkedIn</option>
              <option>X</option>
              <option>Blog</option>
            </select>
          </label>
          <label className="field">Scheduled for
            <input type="datetime-local" value={when} onChange={(e) => setWhen(e.target.value)} />
          </label>
          <label className="field" style={{ flex: 2 }}>Notes
            <input value={notes} onChange={(e) => setNotes(e.target.value)} placeholder="Repurpose top topic…" />
          </label>
        </div>
        <p style={{ marginBottom: 0 }}><button className="btn" onClick={schedule}>Schedule</button></p>
        {saved && <p className="muted">{saved}</p>}
      </Card>

      <div className="row" style={{ alignItems: "center" }}>
        <button className="btn ghost small" onClick={() => shift(-1)}>← Prev</button>
        <h2 style={{ margin: 0, flex: 1, textAlign: "center" }}>{MONTHS[month]} {year}</h2>
        <button className="btn ghost small" onClick={() => shift(1)}>Next →</button>
      </div>
      <div className="calgrid" style={{ marginTop: 10 }}>
        {["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"].map((d) => (
          <p key={d} className="lbl" style={{ textAlign: "center" }}>{d}</p>
        ))}
        {cells.map((c, i) => (
          <div key={i} className={"calday" + (c.day === null ? " dim" : "")}>
            {c.day && <span className="d">{c.day}</span>}
            {c.evs.map((e, j) => (
              <div key={j} className="ev" title={`${e.platform} · ${e.notes}`}>
                [{e.platform}] {e.title ?? e.notes}
              </div>
            ))}
          </div>
        ))}
      </div>
      {cal.data.items.length === 0 && <Empty text="Nothing scheduled yet." />}
    </>
  );
}
