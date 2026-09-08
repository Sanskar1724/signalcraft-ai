"""Opportunity engine (§11): 'trending topics relevant to YOU', with WHY.

Opportunity Score (weights configurable via OPP_WEIGHTS_JSON):
  score = 100 * (w_trend*norm_trend + w_user_rel*user_relevance
                 + w_aud*audience_fit + w_fresh*freshness
                 + w_lowcomp*(1-competition)) + memory_boost
"""
from __future__ import annotations

import json

from .config import settings
from .content.sanitize import leak_found, scrub
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


def _clean_angle(gateway: LLMGateway, profile, topic: str) -> str:
    """One clean sentence, never reasoning. Deterministic fallback on any doubt."""
    import re as _re
    fallback = (f"How {topic} changes day-to-day work "
                f"for {profile.audience or 'your audience'}.")
    try:
        raw = gateway.generate(
            f"Topic: {topic}. Reply with EXACTLY ONE sentence (max 25 words): "
            f"a sharp content angle. No preamble, no bullets, no quotes.",
            task="strategy", max_tokens=80).strip()
    except Exception:
        return fallback
    text = scrub(raw)
    # Keep the first real sentence only.
    sentences = [s.strip().strip("\"'“”") for s in _re.split(r"(?<=[.!?])\s+", text) if s.strip()]
    first = sentences[0] if sentences else ""
    if len(first) < 12 or leak_found(first):
        return fallback
    return first[:200]


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
        comp_word = "low" if t["competition"] < 0.34 else ("medium" if t["competition"] < 0.67 else "high")
        momentum_word = "rising fast" if t["growth"] >= 0.6 else ("steady" if t["growth"] >= 0.3 else "early")
        ev = t["evidence_titles"][:2]
        why_now = (f"'{t['topic']}' is {momentum_word}: {len(t['evidence'])} recent "
                   f"{'source' if len(t['evidence']) == 1 else 'sources'} mention it"
                   + (f", including “{ev[0]}”" if ev else "")
                   + (f" and “{ev[1]}”" if len(ev) > 1 else "")
                   + f". Competition looks {comp_word}.")
        why_you = (f"Fits your niche in {profile.niche or 'your field'} for "
                   f"{profile.audience or 'your audience'}"
                   + (f" and your goal of {profile.goals}" if profile.goals else "")
                   + ".")
        angle = _clean_angle(gateway, profile, t["topic"])
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


def list_opportunities(user_id: int = 1, limit: int = 20, offset: int = 0,
                       include_dismissed: bool = False) -> list[dict]:
    import json as _json
    conn = get_conn()
    try:
        filt = "" if include_dismissed else "AND status!='dismissed'"
        rows = conn.execute(
            "SELECT * FROM content_opportunities WHERE user_id=? " + filt +
            " ORDER BY score DESC LIMIT ? OFFSET ?",
            (user_id, limit, offset)).fetchall()
        out = [dict(r) for r in rows]
        # Attach human-readable evidence titles (provenance chain stays typed).
        ids: set[int] = set()
        refs: list[list[int]] = []
        for o in out:
            try:
                rr = _json.loads(o.get("research_refs") or "[]")
            except Exception:
                rr = []
            cur = [int(x) for x in rr if isinstance(x, int)]
            refs.append(cur)
            ids.update(cur)
        titles: dict[int, str] = {}
        if ids:
            for r in conn.execute(
                    f"SELECT id, title FROM research_documents WHERE id IN ({','.join('?' * len(ids))})",
                    tuple(ids)).fetchall():
                titles[r["id"]] = r["title"]
        for o, rr in zip(out, refs, strict=True):
            o["evidence_titles"] = [titles[i] for i in rr if i in titles]
        return out
    finally:
        conn.close()
