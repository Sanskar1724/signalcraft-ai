"""Trend intelligence (§10): 'what is trending that matters to THIS creator?'

Trend Score (weights configurable via TREND_WEIGHTS_JSON, default = §10 example):
  trend_score = 100 * (w_growth*growth + w_freshness*freshness
                       + w_relevance*relevance + w_momentum*source_momentum
                       + w_novelty*novelty)

- freshness: recency of supporting research (1.0 = <24h, decays to 0 at 30d)
- growth: mention velocity proxy = min(1, n_mentions / 5)
- relevance: keyword overlap between topic and niche+expertise+topics
- source_momentum: min(1, n_distinct_sources / 3)
- novelty: 1 - similarity to recent content (last 10 titles)
- audience_fit / competition: stored for the opportunity score (§11),
  not part of the trend score.
"""
from __future__ import annotations

import json
import re
from collections import Counter
from datetime import datetime, timezone

from .config import settings
from .db import get_conn, new_uuid
from .profiles import get_profile

__all__ = ["tokenize", "freshness_of", "detect_trends"]

STOP = {"the", "and", "for", "with", "from", "that", "this", "into", "using",
        "how", "are", "was", "were", "have", "has", "will", "over", "more"}


def tokenize(s: str) -> list[str]:
    return [w for w in re.findall(r"[a-zA-Z][a-zA-Z0-9+\-#]*", s.lower())
            if w not in STOP and len(w) > 2]


def freshness_of(published_at: str) -> float:
    try:
        dt = datetime.strptime(published_at[:19], "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
        age_days = max(0.0, (datetime.now(timezone.utc) - dt).total_seconds() / 86400)
    except Exception:
        return 0.5
    return max(0.0, 1.0 - age_days / 30.0)


def detect_trends(user_id: int = 1, top_n: int = 10) -> list[dict]:
    w = settings.trend_weights
    profile = get_profile(user_id)
    niche_keys = set(tokenize(profile.niche + " " + profile.expertise
                              + " " + " ".join(profile.topics)))
    aud_keys = set(tokenize(profile.audience))
    avoid = {a.lower() for a in profile.avoid_topics}

    conn = get_conn()
    try:
        research = [dict(r) for r in conn.execute(
            "SELECT * FROM research_documents WHERE user_id=? ORDER BY id DESC LIMIT 60",
            (user_id,)).fetchall()]
        past_titles = " ".join(
            r["title"] for r in conn.execute(
                "SELECT title FROM content WHERE user_id=? ORDER BY id DESC LIMIT 10",
                (user_id,)).fetchall()).lower()
    finally:
        conn.close()

    if not research:
        return []

    by_id = {r["id"]: r for r in research}
    counter: Counter[str] = Counter()
    evidence: dict[str, list[int]] = {}
    for r in research:
        toks = tokenize(f"{r['title']} {r['summary']}")
        grams = [" ".join(toks[i:i + 2]) for i in range(len(toks) - 1)]
        for g in set(grams):
            if any(a in g for a in avoid if a):
                continue
            counter[g] += 1
            evidence.setdefault(g, []).append(r["id"])

    scored = []
    for topic, mentions in counter.most_common(top_n * 3):
        sup = [by_id[i] for i in evidence[topic][:5] if i in by_id]
        fresh = sum(freshness_of(r["published_at"]) for r in sup) / max(1, len(sup))
        growth = min(1.0, mentions / 5.0)
        tset = set(topic.split())
        relevance = len(tset & niche_keys) / max(1, len(tset)) if niche_keys else 0.3
        if any(pt.lower() in topic or topic in pt.lower() for pt in profile.topics):
            relevance = min(1.0, relevance + 0.2)
        sources = {s.get("source", "") for s in sup}
        momentum = min(1.0, len(sources) / 3.0)
        audience_fit = len(tset & aud_keys) / max(1, len(tset)) if aud_keys else 0.3
        novelty = 0.0 if topic in past_titles else 1.0
        if any(word in past_titles for word in tset):
            novelty = 0.5
        competition = min(1.0, mentions / 8.0)
        trend_score = 100 * (w["growth"] * growth + w["freshness"] * fresh
                             + w["relevance"] * relevance
                             + w["source_momentum"] * momentum + w["novelty"] * novelty)
        scored.append({
            "topic": topic, "freshness": round(fresh, 3), "growth": round(growth, 3),
            "relevance": round(relevance, 3), "source_momentum": round(momentum, 3),
            "novelty": round(novelty, 3), "audience_fit": round(audience_fit, 3),
            "competition": round(competition, 3),
            "trend_score": round(trend_score, 1), "score": round(trend_score, 1),
            "evidence": [s["id"] for s in sup],
            "evidence_titles": [s["title"] for s in sup],
        })
    scored.sort(key=lambda d: d["trend_score"], reverse=True)
    top = scored[:top_n]

    conn = get_conn()
    try:
        conn.execute("DELETE FROM trend_signals WHERE user_id=?", (user_id,))
        for t in top:
            conn.execute(
                "INSERT INTO trend_signals (uuid, user_id, topic, freshness, growth,"
                " relevance, source_momentum, novelty, audience_fit, competition,"
                " trend_score, evidence)"
                " VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                (new_uuid(), user_id, t["topic"], t["freshness"], t["growth"],
                 t["relevance"], t["source_momentum"], t["novelty"], t["audience_fit"],
                 t["competition"], t["trend_score"], json.dumps(t["evidence"])),
            )
        conn.commit()
    finally:
        conn.close()
    return top
