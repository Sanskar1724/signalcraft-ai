"use client";

import { api } from "../../lib/api";
import { Card, Empty, Loading, Pill, Quality, useApi } from "../../components/ui";

export default function LibraryPage() {
  const { data, error, busy } = useApi(() => api.library());

  if (busy) return (<><h1>Content Library</h1><Loading /></>);
  if (error || !data) return (<><h1>Content Library</h1><div className="error">API unavailable: {error}</div></>);

  return (
    <>
      <h1>Content Library</h1>
      <p className="sub">Drafts and published pieces with quality scores.</p>
      {data.length === 0 && <Empty text="Nothing here yet — create your first draft." />}
      {data.map((c) => (
        <Card key={c.id}>
          <div className="row" style={{ alignItems: "center" }}>
            <Pill kind={c.platform}>{c.platform}</Pill>
            <b>{c.title}</b>
            <span style={{ flex: 1 }} />
            <Quality score={c.quality_score} />
          </div>
          <p className="muted">{c.status} · {c.created_at}</p>
        </Card>
      ))}
    </>
  );
}
