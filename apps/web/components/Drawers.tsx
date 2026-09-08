"use client";

import Link from "next/link";
import { api, type Opportunity, type TrendSignal } from "../lib/api";
import { ScoreRing } from "./charts";
import { toast } from "./fx";
import { Modal, Pill, ScoreBar } from "./ui";

export function direction(growth: number): string {
  if (growth >= 0.6) return "↗ Rising quickly";
  if (growth >= 0.3) return "→ Stable";
  return "↓ Cooling";
}

export function TrendDrawer({ trend, opportunities, onClose, onChanged }: {
  trend: TrendSignal | null;
  opportunities: Opportunity[];
  onClose: () => void;
  onChanged: () => void;
}) {
  if (!trend) return null;
  const matched = opportunities.filter(
    (o) => o.topic.includes(trend.topic) || trend.topic.includes(o.topic.split(" ")[0])
  ).slice(0, 3);

  async function save() {
    await api.storeMemory("successful_topic", trend!.topic.toLowerCase(), "saved from trends");
    toast("Saved — similar ideas will rank higher.");
    onChanged();
  }

  async function dismiss() {
    await api.storeMemory("weak_topic", trend!.topic.toLowerCase(), "dismissed in trends");
    toast("Dismissed — similar ideas will rank lower.");
    onClose();
    onChanged();
  }

  return (
    <Modal open title={trend.topic} onClose={onClose}>
      <div className="row" style={{ alignItems: "center" }}>
        <ScoreRing value={trend.trend_score} />
        <div>
          <p className="lbl">Momentum</p>
          <b>{direction(trend.growth)}</b>
          <p className="muted">Growth {trend.growth} · Freshness {trend.freshness}</p>
        </div>
      </div>
      <div className="dims">
        <span>Relevance {trend.relevance}</span>
        <span>Momentum {trend.source_momentum}</span>
        <span>Novelty {trend.novelty}</span>
        <span>Audience fit {trend.audience_fit}</span>
        <span>Competition {trend.competition}</span>
      </div>
      <h2>Why it&apos;s rising</h2>
      <p className="muted">Freshness {trend.freshness} with growth {trend.growth} across {trend.source_momentum > 0.5 ? "multiple" : "few"} sources.</p>
      <h2>Evidence</h2>
      {(trend.evidence_titles ?? []).map((e, i) => (
        <p key={i} className="muted">· {e}</p>
      ))}
      {!(trend.evidence_titles ?? []).length && <p className="muted">No linked evidence.</p>}
      <h2>Content opportunities</h2>
      {matched.map((o) => (
        <div key={o.id} className="row" style={{ alignItems: "center" }}>
          <span style={{ flex: 1 }}>{o.topic} — {o.score}</span>
          <Link href={`/app/create?opp=${o.id}`} className="btn small" style={{ textDecoration: "none" }}>Create</Link>
        </div>
      ))}
      {!matched.length && <p className="muted">No opportunity scored for this topic yet — refresh research.</p>}
      <h2>Recommended platforms</h2>
      <p><Pill kind="LinkedIn">LinkedIn</Pill><Pill kind="X">X</Pill><Pill kind="Blog">Blog</Pill></p>
      <div className="row">
        <button className="btn small" onClick={save}>Save Trend</button>
        <button className="btn ghost small" onClick={dismiss}>Dismiss</button>
        <Link href="/app/agent" className="btn ghost small" style={{ textDecoration: "none" }}>Ask Agent</Link>
      </div>
    </Modal>
  );
}

export function OpportunityDrawer({ opp, onClose, onChanged }: {
  opp: Opportunity | null;
  onClose: () => void;
  onChanged: () => void;
}) {
  if (!opp) return null;

  async function save() {
    await api.storeMemory("successful_topic", opp!.topic.toLowerCase(), "saved opportunity");
    toast("Saved — similar ideas will rank higher.");
    onChanged();
  }

  async function dismiss() {
    await api.dismissOpportunity(opp!.id);
    toast("Dismissed — similar ideas will rank lower.");
    onClose();
    onChanged();
  }

  return (
    <Modal open title={opp.topic} onClose={onClose}>
      <div className="row" style={{ alignItems: "center" }}>
        <ScoreRing value={opp.score} />
        <div>
          <p className="lbl">Opportunity score</p>
          <p className="muted">Trend {opp.trend_score} · Confidence {opp.confidence}</p>
        </div>
      </div>
      <ScoreBar value={opp.user_relevance * 100} />
      <div className="fact"><p className="lbl">Signal — why now</p><p>{opp.why_now}</p></div>
      <div className="interp"><p className="lbl">Creator fit — why you</p><p>{opp.why_you}</p></div>
      <div className="reco"><p className="lbl">Strategy — angle</p><p>{opp.angle}</p></div>
      <div className="dims">
        <span>Audience fit {opp.audience_fit}</span>
        <span>Freshness {opp.freshness}</span>
        <span>Competition {opp.competition}</span>
        <span>Audience {opp.audience}</span>
      </div>
      <p><Pill kind={opp.platform.split(" ")[0]}>{opp.platform}</Pill><Pill>{opp.format}</Pill></p>
      <div className="row">
        <Link href={`/app/create?opp=${opp.id}`} className="btn small" style={{ textDecoration: "none" }}>Create</Link>
        <button className="btn ghost small" onClick={save}>Save</button>
        <button className="btn ghost small" onClick={dismiss}>Dismiss</button>
        <Link href="/app/agent" className="btn ghost small" style={{ textDecoration: "none" }}>Ask Agent</Link>
      </div>
    </Modal>
  );
}
