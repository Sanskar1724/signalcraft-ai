"use client";

import { useState } from "react";
import { api, type CalendarItem } from "../../../lib/api";
import { toast } from "../../../components/fx";
import { Card, Empty, Loading, Modal, Pill, Tabs, useApi } from "../../../components/ui";

function monthCells(year: number, month: number, items: CalendarItem[]) {
  const first = new Date(year, month, 1);
  const startDay = (first.getDay() + 6) % 7; // Monday-first
  const days = new Date(year, month + 1, 0).getDate();
  const cells: { day: number | null; label: string | null; evs: CalendarItem[] }[] = [];
  for (let i = 0; i < startDay; i++) cells.push({ day: null, label: null, evs: [] });
  for (let d = 1; d <= days; d++) {
    const key = `${year}-${String(month + 1).padStart(2, "0")}-${String(d).padStart(2, "0")}`;
    cells.push({ day: d, label: null, evs: items.filter((e) => e.scheduled_for.slice(0, 10) === key) });
  }
  return cells;
}

const MONTHS = ["January", "February", "March", "April", "May", "June",
  "July", "August", "September", "October", "November", "December"];

function weekCells(weekOff: number, items: CalendarItem[]) {
  const now = new Date();
  const monday = new Date(now);
  monday.setDate(now.getDate() - ((now.getDay() + 6) % 7) + weekOff * 7);
  return Array.from({ length: 7 }, (_, i) => {
    const d = new Date(monday);
    d.setDate(monday.getDate() + i);
    const key = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
    return {
      day: d.getDate(),
      label: `${["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"][i]} ${d.getDate()}`,
      evs: items.filter((e) => e.scheduled_for.slice(0, 10) === key),
    };
  });
}

export default function CalendarPage() {
  const cal = useApi(() => api.calendar());
  const opps = useApi(() => api.opportunities());
  const now = new Date();
  const [ym, setYm] = useState<[number, number]>([now.getFullYear(), now.getMonth()]);
  const [platform, setPlatform] = useState("LinkedIn");
  const [when, setWhen] = useState("2026-09-10T10:00");
  const [notes, setNotes] = useState("");
  const [saved, setSaved] = useState("");
  const [view, setView] = useState("Month");
  const [weekOff, setWeekOff] = useState(0);
  const [edit, setEdit] = useState<CalendarItem | null>(null);

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
              <option>Newsletter</option>
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
        <Tabs tabs={["Month", "Week", "Agenda"]} active={view} onChange={setView} />
        <span style={{ flex: 1 }} />
        {view === "Month" && (
          <>
            <button className="btn ghost small" onClick={() => shift(-1)}>← Prev</button>
            <h2 style={{ margin: 0 }}>{MONTHS[month]} {year}</h2>
            <button className="btn ghost small" onClick={() => shift(1)}>Next →</button>
          </>
        )}
        {view === "Week" && (
          <>
            <button className="btn ghost small" onClick={() => setWeekOff(weekOff - 1)}>← Prev</button>
            <button className="btn ghost small" onClick={() => setWeekOff(weekOff + 1)}>Next →</button>
          </>
        )}
      </div>
      {view !== "Agenda" && (
      <div className="calgrid" style={{ marginTop: 10 }}>
        {["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"].map((d) => (
          <p key={d} className="lbl" style={{ textAlign: "center" }}>{d}</p>
        ))}
        {(view === "Month" ? cells : weekCells(weekOff, cal.data.items)).map((c, i) => (
          <div key={i} className={"calday" + (c.day === null ? " dim" : "")}>
            {c.day && <span className="d">{c.label ?? c.day}</span>}
            {c.evs.map((e, j) => (
              <div key={j} className="ev" title={`${e.platform} · ${e.notes} (click to edit)`}
                style={{ cursor: "pointer" }} onClick={() => setEdit({ ...e })}>
                [{e.platform}] {e.title ?? e.notes}
              </div>
            ))}
          </div>
        ))}
      </div>
      )}
      {view === "Agenda" && cal.data.items.map((e, i) => (
        <Card key={i}>
          <div className="row" style={{ alignItems: "center" }}>
            <b>{e.scheduled_for}</b>
            <Pill kind={e.platform}>{e.platform}</Pill>
            <span>{e.title ?? e.notes}</span>
            <span style={{ flex: 1 }} />
            <span className="muted">{e.status}</span>
            <button className="btn ghost small" onClick={() => setEdit({ ...e })}>Edit</button>
          </div>
        </Card>
      ))}
      {cal.data.items.length === 0 && <Empty text="Nothing scheduled yet." />}
      <h2>Upcoming opportunities</h2>
      <p className="sub">Top-ranked ideas worth scheduling next.</p>
      {(opps.data ?? []).slice(0, 3).map((o, i) => (
        <Card key={o.id}>
          <p style={{ margin: 0 }}><b>{["Tomorrow", "This week", "Next"][i] ?? "Soon"}</b></p>
          <p style={{ margin: "4px 0" }}>{o.topic} — score {o.score}</p>
          <p className="muted" style={{ margin: 0 }}>Recommended for {o.platform}</p>
        </Card>
      ))}
      {edit && (
        <Modal open onClose={() => setEdit(null)} title="Edit scheduled item">
          <label className="field">Platform
            <select value={edit.platform} onChange={(e) => setEdit({ ...edit, platform: e.target.value })}>
              <option>LinkedIn</option>
              <option>X</option>
              <option>Blog</option>
              <option>Newsletter</option>
            </select>
          </label>
          <label className="field" style={{ marginTop: 10 }}>Scheduled for
            <input type="datetime-local" value={edit.scheduled_for.slice(0, 16).replace(" ", "T")}
              onChange={(e) => setEdit({ ...edit, scheduled_for: e.target.value.replace("T", " ") })} />
          </label>
          <label className="field" style={{ marginTop: 10 }}>Status
            <select value={edit.status} onChange={(e) => setEdit({ ...edit, status: e.target.value })}>
              <option>draft</option>
              <option>scheduled</option>
              <option>published</option>
              <option>cancelled</option>
            </select>
          </label>
          <label className="field" style={{ marginTop: 10 }}>Notes
            <input value={edit.notes} onChange={(e) => setEdit({ ...edit, notes: e.target.value })} />
          </label>
          <div className="row" style={{ marginTop: 12 }}>
            <button className="btn small" onClick={async () => {
              await api.updateCalendar(edit.id, {
                platform: edit.platform, scheduled_for: edit.scheduled_for,
                status: edit.status, notes: edit.notes,
              });
              toast("Rescheduled.");
              setEdit(null);
              cal.reload();
            }}>Save changes</button>
            <button className="btn ghost small" onClick={async () => {
              await api.duplicateCalendar(edit.id);
              toast("Duplicated as draft.");
              setEdit(null);
              cal.reload();
            }}>Duplicate</button>
            <button className="btn ghost small" onClick={async () => {
              await api.updateCalendar(edit.id, { status: "published" });
              toast("Marked published.");
              setEdit(null);
              cal.reload();
            }}>Mark published</button>
          </div>
        </Modal>
      )}
    </>
  );
}
