"use client";

import Link from "next/link";
import { useState } from "react";
import { api } from "../../../lib/api";
import { toast } from "../../../components/fx";
import { Card, Empty, Loading, Pill, ScoreBar, Tabs, useApi } from "../../../components/ui";

function sourcesOf(o: { research_refs?: string }): number {
  try {
    const v = JSON.parse(o.research_refs ?? "[]");
    return Array.isArray(v) ? v.length : 0;
  } catch {
    return 0;
  }
}

export default function OpportunitiesPage() {
  const { data, error, busy, reload } = useApi(() => api.opportunities());
  const [plat, setPlat] = useState("All");
  const [sort, setSort] = useState<"score" | "confidence" | "trend_score">("score");

  if (busy) return (<><h1>Content Opportunities</h1><Loading /></>);
  if (error || !data) return (<><h1>Content Opportunities</h1><div className="error">We couldn&apos;t load your opportunities.
    <p><button className="btn small" onClick={reload}>Retry</button></p></div></>);

  const rows = data
    .filter((o) => plat === "All" || o.platform.includes(plat))
    .sort((a, b) => b[sort] - a[sort]);

  return (
    <>
      <h1>Personalized opportunities</h1>
      <p className="sub">Trending topics relevant to YOU — each with its reason.</p>
      <div className="row">
        <Tabs tabs={["All", "LinkedIn", "X", "Blog"]} active={plat} onChange={setPlat} />
        <Tabs tabs={["score", "confidence", "trend_score"]} active={sort} onChange={(t) => setSort(t as typeof sort)} />
      </div>
      {rows.length === 0 && <Empty text="No opportunities match — clear the filters." />}
      {rows.map((o) => (
        <Card key={o.id} lift>
          <h3>{o.topic}</h3>
          <div className="row" style={{ alignItems: "center" }}>
            <span className="muted">Opportunity</span>
            <div style={{ flex: 1 }}><ScoreBar value={o.score} /></div>
            <b>{o.score}</b>
          </div>
          <div className="fact"><p className="lbl">Observed fact</p><p>{o.why_now}</p></div>
          <div className="interp"><p className="lbl">AI interpretation</p><p>{o.why_you}</p></div>
          <div className="reco"><p className="lbl">AI recommendation</p><p>Angle: {o.angle}</p></div>
          <div className="row" style={{ alignItems: "center" }}>
            <Pill>trend {o.trend_score}</Pill>
            <Pill>relevance {o.user_relevance}</Pill>
            <Pill>audience {o.audience_fit}</Pill>
            <Pill>competition {o.competition}</Pill>
            <Pill kind={o.platform.split(" ")[0]}>{o.platform}</Pill>
            <Pill>{sourcesOf(o)} sources</Pill>
            <span style={{ flex: 1 }} />
            <Link href={`/app/create?opp=${o.id}`} className="btn small" style={{ textDecoration: "none" }}>Create</Link>
            <Link href={`/app/agent`} className="btn ghost small" style={{ textDecoration: "none" }}>Ask Agent</Link>
            <button className="btn ghost small" onClick={async () => {
              await api.dismissOpportunity(o.id);
              toast("Dismissed — similar ideas will rank lower.");
              reload();
            }}>Dismiss</button>
          </div>
        </Card>
      ))}
    </>
  );
}
