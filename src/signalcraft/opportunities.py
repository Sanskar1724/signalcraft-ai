"""Opportunity engine: personalized, explainable recommendations."""
from __future__ import annotations

import json

from .db import get_conn
from .llm import LLMGateway
from .memory import get_memory_boost
from .profiles import get_profile
from .trends import detect_trends

PLATFORM_BY_SCORE = [(80, "LinkedIn + X"), (55, "LinkedIn"), (0, "Blog")]


def _platform(score: float) -> str:
    for cutoff, name in PLATFORM_BY_SCORE:
        if score >= cutoff:
            return name
    return "Blog"


def build_opportunities(user_id: int = 1, top_n: int = 8,
                        gateway: LLMGateway | None = None) -> list[dict]:
    profile = get_profile(user_id)
    trends = detect_trends(user_id=user_id, top_n=top_n * 2)
    gateway = gateway or LLMGateway()

    opps = []
    for t in trends[:top_n]:
        boost = get_memory_boost(user_id, t["topic"])
        score = round(max(0, min(100, t["score"] + boost)), 1)
        confidence = round(max(0.2, min(0.95,
            0.30 + 0.20 * t["relevance"] + 0.15 * t.get("audience_fit", 0)
            + 0.15 * t.get("creator_fit", 0) + 0.10 * t["freshness"]
            + 0.10 * t["novelty"])), 2)
        why_now = (f"'{t['topic']}' appears in {len(t['evidence'])} recent item(s) "
                   f"(freshness {t['freshness']}, growth {t['growth']}, "
                   f"competition {t.get('competition', 0)}). "
                   f"Top evidence: {'; '.join(t['evidence_titles'][:2])}")
        why_you = (f"Matches your niche '{profile.niche or '—'}' "
                   f"(relevance {t['relevance']}, creator fit {t.get('creator_fit', 0)}, "
                   f"audience fit {t.get('audience_fit', 0)}). "
                   f"Audience: {profile.audience or '—'}.")
        angle_prompt = (
            f"Creator niche: {profile.niche}. Expertise: {profile.expertise}. "
            f"Tone: {profile.tone}. Topic: {t['topic']}. "
            f"Suggest one sharp content angle in one sentence."
        )
        try:
            angle = gateway.generate(angle_prompt, task="strategy", max_tokens=120).strip()
        except Exception:
            angle = f"How {t['topic']} changes day-to-day work for {profile.audience or 'your audience'}."
        opps.append({
            "topic": t["topic"], "why_now": why_now, "why_you": why_you,
            "audience": profile.audience or "Your audience",
            "angle": angle, "format": "Insight + example + takeaway",
            "platform": _platform(score), "score": score, "confidence": confidence,
            "research_refs": t["evidence"],
        })

    opps.sort(key=lambda d: d["score"], reverse=True)
    conn = get_conn()
    try:
        conn.execute("DELETE FROM opportunities WHERE user_id=? AND status='new'", (user_id,))
        for o in opps:
            conn.execute(
                "INSERT INTO opportunities (user_id, topic, why_now, why_you, audience,"
                " angle, format, platform, score, confidence, research_refs)"
                " VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                (user_id, o["topic"], o["why_now"], o["why_you"], o["audience"],
                 o["angle"], o["format"], o["platform"], o["score"],
                 o["confidence"], json.dumps(o["research_refs"])),
            )
        conn.commit()
        rows = conn.execute(
            "SELECT * FROM opportunities WHERE user_id=? ORDER BY score DESC LIMIT ?",
            (user_id, top_n)).fetchall()
        ranked = [dict(r) for r in rows]
        # recommendations log (§20): ranked snapshot of this run
        conn.execute("DELETE FROM recommendations WHERE user_id=? AND status='suggested'",
                     (user_id,))
        for i, r in enumerate(ranked, start=1):
            conn.execute(
                "INSERT INTO recommendations (user_id, opportunity_id, reason, rank)"
                " VALUES (?,?,?,?)",
                (user_id, r["id"], f"Ranked #{i} at {r['score']}/100", i),
            )
        conn.commit()
        return ranked
    finally:
        conn.close()


def list_opportunities(user_id: int = 1, limit: int = 20, offset: int = 0) -> list[dict]:
    conn = get_conn()
    try:
        rows = conn.execute(
            "SELECT * FROM opportunities WHERE user_id=? ORDER BY score DESC LIMIT ? OFFSET ?",
            (user_id, limit, offset)).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()
