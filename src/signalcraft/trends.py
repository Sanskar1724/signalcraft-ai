"""Trend intelligence: 'what is trending that matters to THIS creator?'

Transparent formula (documented, testable):
  score = 100 * (0.30*freshness + 0.25*growth + 0.25*relevance + 0.20*novelty)

- freshness: recency of supporting research (1.0 = <24h, decays linearly to 0 at 30d)
- growth: mention velocity proxy = min(1, n_mentions / 5)
- relevance: keyword overlap between topic and creator profile
- novelty: 1 - similarity to recent content topics (MVP: 1 - overlap with last 10 content titles)
"""
from __future__ import annotations

import json
import re
from collections import Counter
from datetime import datetime, timezone

from .db import get_conn
from .profiles import get_profile

STOP = {"the", "and", "for", "with", "from", "that", "this", "into", "using",
        "how", "are", "was", "were", "have", "has", "will", "over", "more"}


def _tokens(s: str) -> list[str]:
    return [w for w in re.findall(r"[a-zA-Z][a-zA-Z0-9+\-#]*", s.lower()) if w not in STOP and len(w) > 2]


def _freshness(published_at: str) -> float:
    try:
        dt = datetime.strptime(published_at[:19], "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
        age_days = max(0.0, (datetime.now(timezone.utc) - dt).total_seconds() / 86400)
    except Exception:
        return 0.5
    return max(0.0, 1.0 - age_days / 30.0)


def detect_trends(user_id: int = 1, top_n: int = 10) -> list[dict]:
    profile = get_profile(user_id)
    pkeys = profile.keywords()
    avoid = {a.lower() for a in profile.avoid_topics}

    conn = get_conn()
    try:
        research = [dict(r) for r in conn.execute(
            "SELECT * FROM research_items WHERE user_id=? ORDER BY id DESC LIMIT 60",
            (user_id,)).fetchall()]
        past_titles = " ".join(
            r["title"] for r in conn.execute(
                "SELECT title FROM content_items WHERE user_id=? ORDER BY id DESC LIMIT 10",
                (user_id,)).fetchall()).lower()
    finally:
        conn.close()

    if not research:
        return []

    # candidate topics: most common bigrams + profile topics present in research
    counter: Counter[str] = Counter()
    evidence: dict[str, list[int]] = {}
    for r in research:
        text = f"{r['title']} {r['summary']}"
        toks = _tokens(text)
        grams = [" ".join(toks[i:i + 2]) for i in range(len(toks) - 1)]
        for g in set(grams):
            if any(a in g for a in avoid if a):
                continue
            counter[g] += 1
            evidence.setdefault(g, []).append(r["id"])

    scored = []
    for topic, mentions in counter.most_common(top_n * 3):
        sup = [r for r in research if r["id"] in evidence[topic][:5]]
        fresh = sum(_freshness(r["published_at"]) for r in sup) / max(1, len(sup))
        growth = min(1.0, mentions / 5.0)
        tset = set(topic.split())
        relevance = len(tset & pkeys) / max(1, len(tset)) if pkeys else 0.3
        # boost if topic matches an explicit profile topic
        if any(pt.lower() in topic or topic in pt.lower() for pt in profile.topics):
            relevance = min(1.0, relevance + 0.3)
        novelty = 0.0 if topic in past_titles else 1.0
        if any(w in past_titles for w in tset):
            novelty = 0.5
        score = 100 * (0.30 * fresh + 0.25 * growth + 0.25 * relevance + 0.20 * novelty)
        scored.append({
            "topic": topic, "freshness": round(fresh, 3), "growth": round(growth, 3),
            "relevance": round(relevance, 3), "novelty": round(novelty, 3),
            "score": round(score, 1),
            "evidence": [s["id"] for s in sup],
            "evidence_titles": [s["title"] for s in sup],
        })
    scored.sort(key=lambda d: d["score"], reverse=True)
    top = scored[:top_n]

    conn = get_conn()
    try:
        conn.execute("DELETE FROM trends WHERE user_id=?", (user_id,))
        for t in top:
            conn.execute(
                "INSERT INTO trends (user_id, topic, freshness, growth, relevance, novelty, score, evidence)"
                " VALUES (?,?,?,?,?,?,?,?)",
                (user_id, t["topic"], t["freshness"], t["growth"], t["relevance"],
                 t["novelty"], t["score"], json.dumps(t["evidence"])),
            )
        conn.commit()
    finally:
        conn.close()
    return top
