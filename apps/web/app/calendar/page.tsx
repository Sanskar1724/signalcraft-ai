"use client";

import { useEffect, useState } from "react";
import { api, type CalendarItem } from "../../lib/api";

export default function CalendarPage() {
  const [items, setItems] = useState<CalendarItem[]>([]);

  useEffect(() => {
    api.calendar().then((r) => setItems(r.items)).catch(() => setItems([]));
  }, []);

  return (
    <>
      <h1>Content calendar</h1>
      {items.map((e, i) => (
        <p key={i}>
          <b>{e.scheduled_for}</b> [{e.platform}] {e.title ?? e.notes} <i>{e.status}</i>
        </p>
      ))}
      {items.length === 0 && <p className="muted">Nothing scheduled.</p>}
    </>
  );
}
