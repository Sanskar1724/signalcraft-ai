"""Creator profile: the personal context that drives everything."""
from __future__ import annotations

import json
from dataclasses import dataclass, field

from .db import get_conn

DEFAULT_PROFILE = {
    "niche": "AI + Data Engineering",
    "expertise": "LLMs, AI agents, PySpark, open source",
    "audience": "Developers, students, data engineers",
    "goals": "Personal branding",
    "platforms": ["LinkedIn", "X", "Blog"],
    "tone": "Technical + simple + professional",
    "topics": ["AI agents", "LLMs", "Data engineering", "Open source", "PySpark"],
    "avoid_topics": ["Generic AI hype"],
    "style_notes": "Concrete examples, no fluff.",
    "content_preferences": "Insight posts, tutorials, build-in-public notes",
    "posting_preferences": "3x per week, mornings",
}


@dataclass
class Profile:
    user_id: int = 1
    niche: str = ""
    expertise: str = ""
    audience: str = ""
    goals: str = ""
    platforms: list[str] = field(default_factory=lambda: ["LinkedIn", "X", "Blog"])
    tone: str = ""
    topics: list[str] = field(default_factory=list)
    avoid_topics: list[str] = field(default_factory=list)
    style_notes: str = ""
    content_preferences: str = ""
    posting_preferences: str = ""

    def keywords(self) -> set[str]:
        blob = " ".join([self.niche, self.expertise, " ".join(self.topics)]).lower()
        words = {w.strip(".,#+/()") for w in blob.replace(",", " ").split()}
        return {w for w in words if len(w) > 2}


def get_profile(user_id: int = 1) -> Profile:
    conn = get_conn()
    try:
        row = conn.execute("SELECT * FROM profiles WHERE user_id=?", (user_id,)).fetchone()
        if row is None:
            conn.execute("INSERT INTO profiles (user_id) VALUES (?)", (user_id,))
            conn.commit()
            return Profile(user_id=user_id)
        return Profile(
            user_id=user_id,
            niche=row["niche"] or "", expertise=row["expertise"] or "",
            audience=row["audience"] or "", goals=row["goals"] or "",
            platforms=json.loads(row["platforms"] or '["LinkedIn","X","Blog"]'),
            tone=row["tone"] or "",
            topics=json.loads(row["topics"] or "[]"),
            avoid_topics=json.loads(row["avoid_topics"] or "[]"),
            style_notes=row["style_notes"] or "",
            content_preferences=row["content_preferences"] or "" if "content_preferences" in row.keys() else "",
            posting_preferences=row["posting_preferences"] or "" if "posting_preferences" in row.keys() else "",
        )
    finally:
        conn.close()


def update_profile(user_id: int = 1, **fields) -> Profile:
    allowed = {"niche", "expertise", "audience", "goals", "platforms",
               "tone", "topics", "avoid_topics", "style_notes",
               "content_preferences", "posting_preferences"}
    cols, vals = [], []
    for k, v in fields.items():
        if k not in allowed:
            raise ValueError(f"invalid profile field: {k}")
        if k in {"platforms", "topics", "avoid_topics"} and isinstance(v, list):
            v = json.dumps(v)
        cols.append(f"{k}=?")
        vals.append(v)
    if cols:
        vals.append(user_id)
        conn = get_conn()
        try:
            conn.execute(
                f"UPDATE profiles SET {', '.join(cols)}, updated_at=datetime('now') WHERE user_id=?",
                vals,
            )
            conn.commit()
        finally:
            conn.close()
    return get_profile(user_id)


def seed_default_profile(user_id: int = 1) -> Profile:
    return update_profile(user_id, **DEFAULT_PROFILE)
