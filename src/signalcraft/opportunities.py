"""Opportunity engine (§11): 'trending topics relevant to YOU', with WHY.

Opportunity Score (weights configurable via OPP_WEIGHTS_JSON):
  score = 100 * (w_trend*norm_trend + w_user_rel*user_relevance
                 + w_aud*audience_fit + w_fresh*freshness
                 + w_lowcomp*(1-competition)) + memory_boost
"""
from __future__ import annotations

import json

from .config import settings
from .db import get_conn, new_uuid
from .llm import LLMGateway
from .memory import get_memory_boost
from .profiles import get_profile
from .trends import detect_trends

__all__ = ["build_opportunities", "list_opportunities"]

PLATFORM_BY_SCORE = [(80, "LinkedIn + X"), (55, "LinkedIn"), (0, "Blog")]


def _platform(score: float) -> str:
    for cutoff, name in PLATFORM_BY_SCORE:
        if score >= cutoff:
            return name
    return "Blog"


def build_opportunities(user_id: int = 1, top_n: int = 8,
                        gateway: LLMGateway | None = None) -> list[dict]:
    w = settings.opp_weights
    profile = get_profile(user_id)
    trends = detect_trends(user_id=user_id, top_n=top_n * 2)
    gateway = gateway or LLMGateway()

    opps = []
    for t in trends[:top_n]:
        user_rel = t["relevance"]
        base = 100 * (w["trend"] * t["trend_score"] / 100.0
                      + w["user_relevance"] * user_rel
                      + w["audience_fit"] * t["audience_fit"]
                      + w["freshness"] * t["freshness"]
                      + w["low_competition"] * (1 - t["competition"]))
        score = round(max(0, min(100, base + get_memory_boost(user_id, t["topic"]))), 1)
        confidence = round(max(0.2, min(0.95,
            0.30 + 0.20 * user_rel + 0.15 * t["audience_fit"]
            + 0.15 * t["trend_score"] / 100.0 + 0.10 * t["freshness"]
            + 0.10 * t["novelty"])), 2)
        why_now = (f"'{t['topic']}' scores {t['trend_score']}/100 "
                   f"(growth {t['growth']}, freshness {t['freshness']}, "
                   f"momentum {t['source_momentum']}, competition {t['competition']}). "
                   f"Top evidence: {'; '.join(t['evidence_titles'][:2])}")
        why_you = (f"Matches your niche '{profile.niche or '—'}' "
                   f"(user relevance {user_rel}, audience fit {t['audience_fit']}). "
                   f"Audience: {profile.audience or '—'}.")
        angle_prompt = (
            f"Creator niche: {profile.niche}. Expertise: {profile.expertise}. "
            f"Tone: {profile.tone}. Topic: {t['topic']}. "
            f"Suggest one sharp content angle in one sentence."
        )
        try:
            angle = gateway.generate(angle_prompt, task="strategy", max_tokens=120).strip()
        except Exception:
            angle = (f"How {t['topic']} changes day-to-day work "
                     f"for {profile.audience or 'your audience'}.")
        opps.append({
            "topic": t["topic"], "trend_score": t["trend_score"],
            "user_relevance": user_rel, "audience_fit": t["audience_fit"],
            "freshness": t["freshness"], "competition": t["competition"],
            "why_now": why_now, "why_you": why_you,
            "audience": profile.audience or "Your audience",
            "angle": angle, "format": "Insight + example + takeaway",
            "platform": _platform(score), "score": score, "confidence": confidence,
            "research_refs": t["evidence"],
        })

    opps.sort(key=lambda d: d["score"], reverse=True)
    conn = get_conn()
    try:
        conn.execute("DELETE FROM content_opportunities WHERE user_id=? AND status='new'",
                     (user_id,))
        for o in opps:
            conn.execute(
                "INSERT INTO content_opportunities (uuid, user_id, topic, trend_score,"
                " user_relevance, audience_fit, freshness, competition, why_now, why_you,"
                " audience, angle, format, platform, score, confidence, research_refs)"
                " VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (new_uuid(), user_id, o["topic"], o["trend_score"], o["user_relevance"],
                 o["audience_fit"], o["freshness"], o["competition"], o["why_now"],
                 o["why_you"], o["audience"], o["angle"], o["format"], o["platform"],
                 o["score"], o["confidence"], json.dumps(o["research_refs"])),
            )
        conn.commit()
        rows = conn.execute(
            "SELECT * FROM content_opportunities WHERE user_id=? ORDER BY score DESC LIMIT ?",
            (user_id, top_n)).fetchall()
        ranked = [dict(r) for r in rows]
        conn.execute("DELETE FROM recommendations WHERE user_id=? AND status='suggested'",
                     (user_id,))
        for i, r in enumerate(ranked, start=1):
            conn.execute(
                "INSERT INTO recommendations (uuid, user_id, opportunity_id, reason, rank)"
                " VALUES (?,?,?,?,?)",
                (new_uuid(), user_id, r["id"], f"Ranked #{i} at {r['score']}/100", i),
            )
        conn.commit()
        return ranked
    finally:
        conn.close()


def list_opportunities(user_id: int = 1, limit: int = 20, offset: int = 0) -> list[dict]:
    conn = get_conn()
    try:
        rows = conn.execute(
            "SELECT * FROM content_opportunities WHERE user_id=? ORDER BY score DESC"
            " LIMIT ? OFFSET ?",
            (user_id, limit, offset)).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()
