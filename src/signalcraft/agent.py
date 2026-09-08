"""Content agent (§11, §18): controlled workflow, tool-using, observable (§24).

Pipeline (bounded: max 8 tool calls, 1 revise loop):
  intent -> creator profile -> memory -> research -> trends/opps ->
  strategy -> content/critique -> store -> answer.
Data questions always hit the DB first — never model knowledge alone (§18).
"""
from __future__ import annotations

from . import analytics as _an
from .content.generator import generate_content
from .llm import LLMGateway
from .memory import recall
from .observability import Trace
from .opportunities import list_opportunities
from .profiles import get_profile
from .research import list_recent, search
from .security import MAX_TOOL_CALLS, Budget, check_rate_limit, validate_request

__all__ = ["classify_intent", "run", "list_opportunities_for_actions"]


def list_opportunities_for_actions(intent: str, user_id: int = 1) -> list[dict]:
    """Action buttons for chat answers (§15): real deep links, never decorative."""
    if intent in {"trends", "ideas", "recommend", "why", "angle"}:
        top = list_opportunities(user_id)[:1]
        if not top:
            return [{"label": "Explore trends", "href": "/app/trends"}]
        oid = top[0]["id"]
        return [
            {"label": "Create content", "href": f"/app/create?opp={oid}"},
            {"label": "View opportunity", "href": "/app/opportunities"},
        ]
    if intent in {"transform_linkedin", "transform_x", "transform_blog"}:
        return [{"label": "Open library", "href": "/app/library"}]
    if intent == "analyze":
        return [{"label": "View analytics", "href": "/app/analytics"}]
    return []


def classify_intent(text: str) -> str:
    t = text.lower()
    if any(k in t for k in ["why did", "perform poorly", "analyze", "last 10", "last 5", "analytics"]):
        return "analyze"
    if any(k in t for k in ["linkedin", "turn this into", "make this into"]) and "linkedin" in t:
        return "transform_linkedin"
    if "x thread" in t or ("thread" in t) or ("twitter" in t) or (t.strip().startswith("x ") ):
        return "transform_x"
    if "blog" in t and any(k in t for k in ["turn", "make", "into", "write"]):
        return "transform_blog"
    if "trending" in t or "niche" in t:
        return "trends"
    if "angle" in t or "technical angle" in t:
        return "angle"
    if "week" in t or "ideas" in t or "content ideas" in t:
        return "ideas"
    if "today" in t or "post today" in t or "what should i" in t:
        return "recommend"
    if text.strip().startswith("Why is") or "relevant to me" in t:
        return "why"
    return "general"


def run(request: str, user_id: int = 1, gateway: LLMGateway | None = None) -> dict:
    request = validate_request(request)
    check_rate_limit(f"agent:{user_id}")
    budget = Budget()
    gateway = gateway or LLMGateway()
    trace = Trace(request)
    from .personalization import build_context
    ctx = build_context(user_id)
    profile = get_profile(user_id)
    trace.add("understand_request", classify_intent(request))
    trace.add("creator_context", {
        "name": ctx["user"]["name"], "niche": ctx["niche"], "audience": ctx["audience"],
        "goals": ctx["goals"], "tone": ctx["tone"], "platforms": ctx["platforms"],
        "posts": ctx["posts"], "best_topics": ctx["best_topics"],
        "memories": ctx["memories"][:5],
    })
    mem = recall(user_id, limit=5)
    trace.add("memory", [f"{m['kind']}:{m['key']}" for m in mem])

    intent = classify_intent(request)
    calls = 0

    def tool(name: str, detail=None):
        nonlocal calls
        calls += 1
        budget.check()
        if calls > MAX_TOOL_CALLS:
            raise RuntimeError(f"tool budget exceeded (max {MAX_TOOL_CALLS})")
        trace.add(f"tool:{name}", detail)

    if intent == "analyze":
        tool("analytics.summary")
        s = _an.summary(user_id)
        tool("analytics.insights")
        ins = _an.insights(user_id)
        answer = ("Observed fact: " + (f"{s['posts']} posts, avg engagement {s['avg_engagement']}%." if s["posts"]
                  else "no posts tracked yet.") + "\nInterpretation: " +
                  ("; ".join(ins) if ins else "not enough data.") +
                  "\nRecommendation: double down on your top topic this week and reframe the weakest one.")
        return {"answer": answer, "intent": intent, "trace": trace.to_dict()}

    if intent in {"transform_linkedin", "transform_x", "transform_blog"}:
        tool("opportunities.list")
        opps = list_opportunities(user_id)
        if not opps:
            return {"answer": "No opportunities yet. Refresh research first (Trending page).",
                    "intent": intent, "trace": trace.to_dict()}
        plat = {"transform_linkedin": "LinkedIn", "transform_x": "X",
                "transform_blog": "Blog"}[intent]
        tool("content.generate", {"platform": plat})
        res = generate_content(opps[0]["id"], platform=plat, user_id=user_id,
                               gateway=gateway, trace=trace)
        c = res["content"]
        return {"answer": (f"Observed fact: transformed using your top opportunity '{opps[0]['topic']}'.\n"
                           f"Interpretation: angle fits {profile.audience}.\n"
                           f"Recommendation: review quality {c['quality_score']}/10, then publish.\n\n{c['body'][:1500]}"),
                "intent": intent, "content_id": c["id"], "trace": trace.to_dict()}

    if intent in {"trends", "ideas", "recommend", "why", "angle", "general"}:
        tool("research.search")
        try:
            ev = search(user_id, profile.niche.split("+")[0].strip() or profile.niche) or list_recent(user_id)
        except Exception as e:
            trace.add("tool_error", f"research.search failed: {e}")
            ev = []
        tool("opportunities.list")
        try:
            opps = list_opportunities(user_id)
        except Exception as e:
            trace.add("tool_error", f"opportunities.list failed: {e}")
            opps = []
        trace.add("opportunity_selected", opps[0]["topic"] if opps else None)
        if not opps:
            return {"answer": ("Observed fact: no opportunities scored yet.\n"
                               "Interpretation: research exists but trends not computed.\n"
                               "Recommendation: click 'Refresh research + trends' on the Trending page."),
                    "intent": intent, "trace": trace.to_dict()}
        if intent == "angle":
            tool("strategy.angle")
            from .content.sanitize import scrub as _scrub
            angle = _scrub(gateway.generate(
                f"Creator niche: {profile.niche}. Tone: {profile.tone}. "
                f"Topic: {opps[0]['topic']}. Give a more technical angle in two sentences.",
                task="strategy", max_tokens=150).strip())
            return {"answer": ("Observed fact: top opportunity is "
                               f"'{opps[0]['topic']}' ({opps[0]['score']}/100).\n"
                               f"Interpretation: fits {profile.audience}.\n"
                               f"Recommendation: use this angle:\n\n{angle}"),
                    "intent": intent, "trace": trace.to_dict()}
        top = opps[:3]
        lines = [f"{i+1}. {o['topic']} ({o['score']}/100, conf {o['confidence']}) — {o['angle'][:140]}"
                 for i, o in enumerate(top)]
        src = f" Evidence: {ev[0]['title']} [{ev[0]['source']}]" if ev else ""
        answer = ("Observed fact: top opportunities ranked from your recent research." + src +
                  "\nInterpretation: these best match your niche + audience + memory.\n" +
                  "Recommendation: start with #1 today.\n\n" + "\n".join(lines))
        if intent == "why":
            answer += f"\n\nWhy '{top[0]['topic']}' for you: {top[0]['why_you']}"
        return {"answer": answer, "intent": intent, "trace": trace.to_dict()}

    return {"answer": "I can help with posting ideas, trends, transforms, and performance analysis.",
            "intent": intent, "trace": trace.to_dict()}
