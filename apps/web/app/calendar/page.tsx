"use client";

import { api } from "../../lib/api";
import { Card, Empty, Loading, Pill, useApi } from "../../components/ui";

export default function CalendarPage() {
  const { data, error, busy } = useApi(() => api.calendar());

  if (busy) return (<><h1>Content Calendar</h1><Loading /></>);
  if (error || !data) return (<><h1>Content Calendar</h1><div className="error">API unavailable: {error}</div></>);

  return (
    <>
      <h1>Content Calendar</h1>
      <p className="sub">Planned content, in order.</p>
      {data.items.length === 0 && <Empty text="Nothing scheduled yet." />}
      {data.items.map((e, i) => (
        <Card key={i}>
          <div className="row" style={{ alignItems: "center" }}>
            <b>{e.scheduled_for}</b>
            <Pill kind={e.platform}>{e.platform}</Pill>
            <span>{e.title ?? e.notes}</span>
            <span style={{ flex: 1 }} />
            <span className="muted">{e.status}</span>
          </div>
        </Card>
      ))}
    </>
  );
}
