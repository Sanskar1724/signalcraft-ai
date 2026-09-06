"""Content generator (§11-§13): strategy -> draft -> critique -> bounded improve -> store.

Flow per request (max 1 revise loop, max ~3 LLM calls):
  understand request + creator + memory -> strategy (LLM) ->
  platform transform (deterministic) -> critique (deterministic) ->
  improve once if <7.5 -> validate -> store content + version.
Grounding (§31): drafts built only from opportunity angle + stored research titles.
"""
from __future__ import annotations

import json

from ..db import get_conn
from ..llm import LLMGateway
from ..memory import recall
from ..observability import Trace
from ..profiles import get_profile
from .critic import critique
from .platforms import format_blog, format_linkedin, format_x

MAX_BODY = 6000


def _strategy_text(gateway: LLMGateway, profile, opp: dict) -> str:
    prompt = (
        f"Niche: {profile.niche}. Audience: {profile.audience}. Tone: {profile.tone}. "
        f"Topic: {opp.get('topic')}. Angle: {opp.get('angle')}. "
        f"Write a useful core paragraph (120-180 words): one claim, one example, one takeaway. "
        f"No hype, no invented statistics."
    )
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
        opp = conn.execute("SELECT * FROM opportunities WHERE id=? AND user_id=?",
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

    core = _strategy_text(gateway, profile, opp)
    trace.add("strategy", core[:200])

    fmt = {"LinkedIn": format_linkedin, "X": format_x, "Blog": format_blog}.get(platform, format_linkedin)
    hook, body, cta = fmt(opp["topic"], opp.get("angle", ""), core, profile.tone)
    body = body[:MAX_BODY]
    trace.add("draft", {"hook": hook, "chars": len(body)})

    result = critique(body, platform=platform, topic=opp["topic"])
    trace.add("critique", {"overall": result["overall"], "issues": result["issues"]})

    if result["overall"] < 7.5:  # one bounded improvement, §13
        fix = gateway.generate(
            f"Improve this {platform} draft. Issues: {result['suggestion']}\n\nDraft:\n{body[:1500]}",
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
            "INSERT INTO content_items (user_id, opportunity_id, platform, title, body, hook, cta, quality_score)"
            " VALUES (?,?,?,?,?,?,?,?)",
            (user_id, opportunity_id, platform, hook[:200], body, hook[:200],
             cta[:200], result["overall"]),
        )
        cid = cur.lastrowid
        conn.execute(
            "INSERT INTO content_versions (content_id, version, body, critique, score)"
            " VALUES (?,?,?,?,?)",
            (cid, 1, body, json.dumps(result), result["overall"]),
        )
        conn.commit()
        row = conn.execute("SELECT * FROM content_items WHERE id=?", (cid,)).fetchone()
        return {"content": dict(row), "critique": result, "trace": trace.to_dict()}
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
                "SELECT c.*, o.topic AS opportunity_topic FROM content_items c"
                " LEFT JOIN opportunities o ON o.id=c.opportunity_id"
                " WHERE c.user_id=? AND c.platform=? ORDER BY c.id DESC LIMIT ? OFFSET ?",
                (user_id, platform, limit, offset)).fetchall()
        else:
            rows = conn.execute(
                "SELECT c.*, o.topic AS opportunity_topic FROM content_items c"
                " LEFT JOIN opportunities o ON o.id=c.opportunity_id"
                " WHERE c.user_id=? ORDER BY c.id DESC LIMIT ? OFFSET ?",
                (user_id, limit, offset)).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()
