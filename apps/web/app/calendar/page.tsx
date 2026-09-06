"use client";

import { useState } from "react";
import { api } from "../../lib/api";
import { timeAgo } from "../../components/charts";
import { Card, Empty, Loading, Pill, useApi } from "../../components/ui";

export default function CalendarPage() {
  const cal = useApi(() => api.calendar());
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

  return (
    <>
      <h1>Content Calendar</h1>
      <p className="sub">Plan what ships, where, and when.</p>
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
      {cal.data.items.length === 0 && <Empty text="Nothing scheduled yet." />}
      {cal.data.items.map((e, i) => (
        <Card key={i}>
          <div className="row" style={{ alignItems: "center" }}>
            <b>{e.scheduled_for}</b>
            <Pill kind={e.platform}>{e.platform}</Pill>
            <span>{e.title ?? e.notes}</span>
            <span style={{ flex: 1 }} />
            <span className="muted">{e.status} · {timeAgo(e.scheduled_for)}</span>
          </div>
        </Card>
      ))}
    </>
  );
}
