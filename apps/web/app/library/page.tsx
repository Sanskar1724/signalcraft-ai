"use client";

import { useEffect, useState } from "react";
import { api, type ContentItem } from "../../lib/api";

export default function LibraryPage() {
  const [items, setItems] = useState<ContentItem[]>([]);

  useEffect(() => {
    api.library().then(setItems).catch(() => setItems([]));
  }, []);

  return (
    <>
      <h1>Content library</h1>
      {items.map((c) => (
        <div key={c.id} className="card">
          <b>[{c.platform}] {c.title}</b> — Q{c.quality_score} · {c.status}
          <p className="muted">{c.created_at}</p>
        </div>
      ))}
      {items.length === 0 && <p className="muted">Nothing here yet.</p>}
    </>
  );
}
