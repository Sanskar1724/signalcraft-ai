"""Content generator (§11-§13): strategy -> draft -> critique -> bounded improve -> store.

Flow per request (max 1 revise loop, max ~3 LLM calls):
  understand request + creator + memory -> strategy (LLM) ->
  platform transform (deterministic) -> critique (deterministic) ->
  improve once if <7.5 -> validate -> store content + version.
Grounding (§31): drafts built only from opportunity angle + stored research titles.
"""
from __future__ import annotations

import json

from ..db import get_conn, new_uuid
from ..llm import LLMGateway
from ..llm.prompts import render
from ..llm.schemas import ContentBrief
from ..memory import recall
from ..observability import Trace
from ..profiles import get_profile
from .critic import critique
from .platforms import format_blog, format_linkedin, format_x

MAX_BODY = 6000


def _evidence_titles(opp: dict) -> list[str]:
    """Resolve stored research refs to titles (§33 provenance)."""
    import json as _json
    refs = opp.get("research_refs") or "[]"
    try:
        ids = _json.loads(refs) if isinstance(refs, str) else list(refs)
    except Exception:
        return []
    if not ids:
        return []
    conn = get_conn()
    try:
        rows = conn.execute(
            f"SELECT title FROM research_documents WHERE id IN ({','.join('?' * len(ids))})",
            ids).fetchall()
        return [r["title"] for r in rows]
    finally:
        conn.close()


def build_brief(profile, opp: dict, evidence_titles: list[str],
                prefs: dict | None = None) -> ContentBrief:
    """Structured content brief (§13) built deterministically, LLM drafts from it."""
    prefs = prefs or {}
    cta_by_pref = {
        "question": "What is working for you?",
        "link": "Sources linked below — what did I miss?",
        "follow": "Follow for the next breakdown.",
        "none": "",
    }
    return ContentBrief(
        topic=opp.get("topic", ""),
        target_audience=opp.get("audience", profile.audience),
        platform=opp.get("platform", "LinkedIn"),
        core_message=opp.get("angle", ""),
        angle=opp.get("angle", ""),
        supporting_evidence=evidence_titles[:3],
        cta=cta_by_pref.get(prefs.get("cta_pref", ""), "What is working for you?"),
        tone=prefs.get("tone") or profile.tone,
        things_to_avoid=profile.avoid_topics,
    )


def _strategy_text(gateway: LLMGateway, brief: ContentBrief, tone: str) -> str:
    prompt = render("content_strategy", brief=brief.model_dump_json(), tone=tone or "clear")
    core = gateway.generate(prompt, task="generation", max_tokens=400).strip()
    # Strip mock prefix so UI reads clean; keep provenance in version row instead.
    if core.startswith("[Mock draft"):
        core = core.split("]", 1)[-1].strip()
    return core[:2000]


def generate_content(opportunity_id: int, platform: str = "LinkedIn",
                     user_id: int = 1, gateway: LLMGateway | None = None,
                     trace: Trace | None = None) -> dict:
    gateway = gateway or LLMGateway()
    profile = get_profile(user_id)
    conn = get_conn()
    try:
        opp = conn.execute("SELECT * FROM content_opportunities WHERE id=? AND user_id=?",
                           (opportunity_id, user_id)).fetchone()
        if opp is None:
            raise ValueError(f"opportunity {opportunity_id} not found")
        opp = dict(opp)
    finally:
        conn.close()

    trace = trace or Trace(f"generate:{platform}:{opp['topic']}")
    trace.add("understand_request", {"platform": platform, "topic": opp["topic"]})
    trace.add("creator_context", {"niche": profile.niche, "tone": profile.tone,
                                  "memory": [m["key"] for m in recall(user_id, limit=5)]})

    evidence = _evidence_titles(opp)
    from ..preferences import get_preferences
    brief = build_brief(profile, {**opp, "platform": platform}, evidence,
                        get_preferences(user_id))
    trace.add("brief", brief.model_dump())

    core = _strategy_text(gateway, brief, profile.tone)
    trace.add("strategy", core[:200])

    fmt = {"LinkedIn": format_linkedin, "X": format_x, "Blog": format_blog}.get(platform, format_linkedin)
    hook, body, cta = fmt(opp["topic"], opp.get("angle", ""), core, profile.tone)
    body = body[:MAX_BODY]
    trace.add("draft", {"hook": hook, "chars": len(body)})

    result = critique(body, platform=platform, topic=opp["topic"])
    trace.add("critique", {"overall": result["overall"], "issues": result["issues"]})

    from ..config import settings as _settings
    threshold = _settings.quality_threshold
    for _ in range(max(1, _settings.max_retries)):  # bounded revise loop (§15)
        if result["overall"] >= threshold:
            break
        fix = gateway.generate(
            render("content_revision", platform=platform,
                   issues=result["suggestion"], draft=body[:1500]),
            task="generation", max_tokens=500).strip()
        if fix.startswith("[Mock draft"):
            fix = fix.split("]", 1)[-1].strip()
        body = (body + f"\n\nRefinement: {fix[:800]}")[:MAX_BODY]
        result = critique(body, platform=platform, topic=opp["topic"])
        trace.add("revise", {"overall": result["overall"]})

    validation = validate(body, platform=platform)
    trace.add("validate", validation)
    if not validation["ok"]:
        raise ValueError(f"content validation failed: {validation['errors']}")

    conn = get_conn()
    try:
        cur = conn.execute(
            "INSERT INTO content (uuid, user_id, opportunity_id, platform, title, body,"
            " hook, cta, quality_score)"
            " VALUES (?,?,?,?,?,?,?,?,?)",
            (new_uuid(), user_id, opportunity_id, platform, hook[:200], body, hook[:200],
             cta[:200], result["overall"]),
        )
        cid = cur.lastrowid
        conn.execute(
            "INSERT INTO content_versions (uuid, content_id, version, brief, body, critique, score)"
            " VALUES (?,?,?,?,?,?,?)",
            (new_uuid(), cid, 1, brief.model_dump_json(), body,
             json.dumps(result), result["overall"]),
        )
        conn.commit()
        row = conn.execute("SELECT * FROM content WHERE id=?", (cid,)).fetchone()
        return {"content": dict(row), "critique": result, "brief": brief,
                "trace": trace.to_dict()}
    finally:
        conn.close()


def validate(body: str, platform: str = "LinkedIn") -> dict:
    """Final validation gate (§11): non-empty, within caps, platform sane."""
    errors = []
    text = (body or "").strip()
    if len(text) < 40:
        errors.append("body too short (<40 chars)")
    if len(text) > MAX_BODY:
        errors.append(f"body exceeds {MAX_BODY} chars")
    if platform not in {"LinkedIn", "X", "Blog"}:
        errors.append(f"unknown platform: {platform}")
    return {"ok": not errors, "errors": errors}


def list_content(user_id: int = 1, limit: int = 50, offset: int = 0,
                 platform: str | None = None) -> list[dict]:
    conn = get_conn()
    try:
        if platform:
            rows = conn.execute(
                "SELECT c.*, o.topic AS opportunity_topic FROM content c"
                " LEFT JOIN content_opportunities o ON o.id=c.opportunity_id"
                " WHERE c.user_id=? AND c.platform=? ORDER BY c.id DESC LIMIT ? OFFSET ?",
                (user_id, platform, limit, offset)).fetchall()
        else:
            rows = conn.execute(
                "SELECT c.*, o.topic AS opportunity_topic FROM content c"
                " LEFT JOIN content_opportunities o ON o.id=c.opportunity_id"
                " WHERE c.user_id=? ORDER BY c.id DESC LIMIT ? OFFSET ?",
                (user_id, limit, offset)).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()
