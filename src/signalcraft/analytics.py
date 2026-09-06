"""Performance analytics (§15-§16). Manual entry MVP, deterministic insights."""
from __future__ import annotations

from statistics import mean

from .db import get_conn


def engagement_rate(impressions: int, likes: int, comments: int,
                    shares: int, saves: int, clicks: int = 0) -> float:
    if impressions <= 0:
        return 0.0
    return round(100 * (likes + comments + shares + saves + clicks) / impressions, 2)


def record_performance(content_id: int, platform: str = "", impressions: int = 0,
                       likes: int = 0, comments: int = 0, shares: int = 0,
                       clicks: int = 0, saves: int = 0) -> dict:
    for name, v in {"impressions": impressions, "likes": likes, "comments": comments,
                    "shares": shares, "clicks": clicks, "saves": saves}.items():
        if v < 0:
            raise ValueError(f"{name} must be >= 0")
    er = engagement_rate(impressions, likes, comments, shares, saves, clicks)
    conn = get_conn()
    try:
        conn.execute(
            "INSERT INTO performance (content_id, platform, impressions, likes, comments,"
            " shares, clicks, saves, engagement_rate) VALUES (?,?,?,?,?,?,?,?,?)",
            (content_id, platform, impressions, likes, comments, shares, clicks, saves, er),
        )
        conn.commit()
        row = conn.execute("SELECT * FROM performance WHERE content_id=? ORDER BY id DESC LIMIT 1",
                           (content_id,)).fetchone()
        return dict(row)
    finally:
        conn.close()


def summary(user_id: int = 1) -> dict:
    conn = get_conn()
    try:
        rows = [dict(r) for r in conn.execute(
            "SELECT c.id, c.platform, c.title, o.topic AS topic,"
            " COALESCE(p.impressions,0) AS impressions, COALESCE(p.likes,0) AS likes,"
            " COALESCE(p.comments,0) AS comments, COALESCE(p.shares,0) AS shares,"
            " COALESCE(p.engagement_rate,0) AS engagement_rate"
            " FROM content_items c LEFT JOIN opportunities o ON o.id=c.opportunity_id"
            " LEFT JOIN (SELECT content_id, MAX(id) AS mid FROM performance GROUP BY content_id) latest"
            " ON latest.content_id=c.id LEFT JOIN performance p ON p.id=latest.mid"
            " WHERE c.user_id=? ORDER BY c.id DESC LIMIT 100", (user_id,)).fetchall()]
    finally:
        conn.close()

    def agg(key: str) -> list[dict]:
        groups: dict[str, list[float]] = {}
        for r in rows:
            k = str(r.get(key) or "Unknown")
            groups.setdefault(k, []).append(float(r.get("engagement_rate") or 0))
        out = [{"topic" if key == "topic" else key: k,
                "posts": len(v), "avg_engagement": round(mean(v), 2)} for k, v in groups.items()]
        out.sort(key=lambda d: d["avg_engagement"], reverse=True)
        return out

    by_topic = agg("topic")
    return {
        "posts": len(rows),
        "rows": rows,
        "avg_engagement": round(mean([r["engagement_rate"] for r in rows]), 2) if rows else 0.0,
        "best_topics": by_topic[:3],
        "weak_topics": by_topic[-3:][::-1] if len(by_topic) > 1 else [],
        "by_platform": agg("platform"),
    }


def insights(user_id: int = 1) -> list[str]:
    """Deterministic creator insights for the Insights page + learning loop."""
    s = summary(user_id)
    out: list[str] = []
    if not s["posts"]:
        return ["Publish your first piece, then log performance to unlock insights."]
    out.append(f"{s['posts']} posts tracked. Average engagement {s['avg_engagement']}%.")
    if s["best_topics"]:
        b = s["best_topics"][0]
        out.append(f"Best topic: '{b['topic']}' at {b['avg_engagement']}% over {b['posts']} post(s). Do more of this.")
    if s["weak_topics"] and len(s.get("best_topics", [])) > 1:
        w = s["weak_topics"][0]
        out.append(f"Weakest topic: '{w['topic']}' at {w['avg_engagement']}%. Reframe or pause it.")
    if s["by_platform"]:
        p = s["by_platform"][0]
        out.append(f"Strongest platform: {p.get('platform', p)} at {p['avg_engagement']}%. Prioritize it this week.")
    return out
