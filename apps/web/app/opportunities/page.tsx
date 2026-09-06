"use client";

import { api } from "../../lib/api";
import { Card, Empty, Loading, Pill, ScoreBar, useApi } from "../../components/ui";

export default function OpportunitiesPage() {
  const { data, error, busy } = useApi(() => api.opportunities());

  if (busy) return (<><h1>Content Opportunities</h1><Loading /></>);
  if (error || !data) return (<><h1>Content Opportunities</h1><div className="error">API unavailable: {error}</div></>);

  return (
    <>
      <h1>Personalized opportunities</h1>
      <p className="sub">Trending topics relevant to YOU — each with its reason.</p>
      {data.length === 0 && <Empty text="No opportunities yet." />}
      {data.map((o) => (
        <Card key={o.id}>
          <h3>{o.topic}</h3>
          <div className="row" style={{ alignItems: "center" }}>
            <span className="muted">Opportunity</span>
            <div style={{ flex: 1 }}><ScoreBar value={o.score} /></div>
            <b>{o.score}</b>
          </div>
          <div className="fact"><p className="lbl">Observed fact</p><p>{o.why_now}</p></div>
          <div className="interp"><p className="lbl">AI interpretation</p><p>{o.why_you}</p></div>
          <div className="reco"><p className="lbl">AI recommendation</p><p>Angle: {o.angle}</p></div>
          <div style={{ marginTop: 8 }}>
            <Pill>trend {o.trend_score}</Pill>
            <Pill>relevance {o.user_relevance}</Pill>
            <Pill>audience {o.audience_fit}</Pill>
            <Pill>competition {o.competition}</Pill>
            <Pill kind={o.platform.split(" ")[0]}>{o.platform}</Pill>
          </div>
        </Card>
      ))}
    </>
  );
}
