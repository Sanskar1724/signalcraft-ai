"""Onboarding flow (§3-§11): stepwise profile building persisted per step.

POST /api/onboarding accepts any subset; complete() validates the minimum
(name + niche), flips status to COMPLETED and builds initial intelligence.
"""
from __future__ import annotations

from . import preferences as _prefs
from .auth import get_user, set_onboarding_status
from .profiles import get_profile, update_profile
from .taxonomy import save_audience, save_topic

__all__ = ["apply_step", "complete", "get_status"]

REQUIRED_FOR_COMPLETE = ("name_set", "niche_set")


def get_status(user_id: int = 1) -> dict:
    user = get_user(user_id)
    profile = get_profile(user_id)
    return {
        "status": user["onboarding_status"],
        "name_set": bool(user["name"] and user["name"] != "Creator"),
        "niche_set": bool(profile.niche),
    }


def _as_list(v) -> list[str]:
    if v is None:
        return []
    if isinstance(v, list):
        return [str(x).strip() for x in v if str(x).strip()]
    return [s.strip() for s in str(v).split(",") if s.strip()]


def apply_step(user_id: int = 1, **payload) -> dict:
    """Persist one wizard step. Unknown keys raise; known keys route to
    profile / preferences / taxonomy. Always marks IN_PROGRESS."""
    from .db import get_conn
    profile_fields = {}
    for key in ("niche", "expertise", "expertise_level", "audience", "goals",
                "platforms", "writing_style", "tone", "topics", "avoid_topics",
                "style_notes", "content_preferences", "posting_preferences",
                "role", "bio", "location"):
        if key in payload and payload[key] is not None:
            profile_fields[key] = payload[key]
    if "goals" in profile_fields and isinstance(profile_fields["goals"], list):
        profile_fields["goals"] = ", ".join(profile_fields["goals"])
    if payload.get("name"):
        conn = get_conn()
        try:
            conn.execute("UPDATE users SET name=? WHERE id=?",
                         (str(payload["name"]).strip(), user_id))
            conn.commit()
        finally:
            conn.close()
    if profile_fields:
        update_profile(user_id, **profile_fields)
    pref_fields = {k: payload[k] for k in _prefs.DEFAULT_PREFS
                   if k in payload and payload[k] is not None}
    if pref_fields:
        _prefs.update_preferences(user_id, **pref_fields)
    for aud in _as_list(payload.get("audience_segments")):
        save_audience(user_id, aud)
    for topic in _as_list(payload.get("secondary_topics")):
        save_topic(user_id, topic)
    for topic in _as_list(payload.get("avoid_topics_extra")):
        save_topic(user_id, topic, status="avoided")
    set_onboarding_status(user_id, "IN_PROGRESS")
    return get_status(user_id)


def complete(user_id: int = 1) -> dict:
    """Validate, build initial intelligence, mark COMPLETED."""
    from . import jobs
    from .taxonomy import sync_profile_taxonomy
    status = get_status(user_id)
    missing = [k for k in REQUIRED_FOR_COMPLETE if not status[k]]
    if missing:
        raise ValueError(f"complete your profile first: missing {', '.join(missing)}")
    sync_profile_taxonomy(user_id)
    built = jobs.run_refresh(user_id=user_id, limit=20, use_live=True, timeout=6)
    user = set_onboarding_status(user_id, "COMPLETED")
    profile = get_profile(user_id)
    return {
        "status": user["onboarding_status"],
        "summary": {
            "niche": profile.niche, "audience": profile.audience,
            "goals": profile.goals, "style": profile.tone or profile.writing_style,
            "platforms": profile.platforms,
        },
        "built": built,
    }
