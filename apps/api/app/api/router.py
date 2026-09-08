"""REST routes (§23, §30-§32). All errors use the envelope from core.errors."""
from __future__ import annotations

import urllib.parse

from fastapi import APIRouter, Depends, Header

from ..analytics.service import insights, summary
from ..api.deps import current_request_id, get_user_id, require_key
from ..core.config import API_PREFIX
from ..models.models import (
    ChatOut,
    ContentDetail,
    ContentItem,
    Opportunity,
    Performance,
    ProfileOut,
    TrendSignal,
)
from ..repositories.content import get_content_detail
from ..schemas.schemas import (
    CalendarUpdate,
    ChatIn,
    CritiqueIn,
    GenerateIn,
    ImproveIn,
    LoginIn,
    MemoryIn,
    OnboardingStep,
    PasswordIn,
    PerformanceIn,
    PreferencesUpdate,
    ProfileUpdate,
    ResearchRun,
    RestoreIn,
    ReviseIn,
    SaveIn,
    ScheduleIn,
    SignupIn,
    StatusIn,
)
from ..services.services import (
    agent,
    content,
    context,
    identity,
    onboarding,
    opportunity,
    preferences,
    profile,
    research,
    trend,
)

router = APIRouter(prefix=API_PREFIX, dependencies=[Depends(require_key)])
public = APIRouter(prefix=API_PREFIX)


@public.post("/auth/signup")
async def post_signup(body: SignupIn) -> dict:
    return identity.signup(body.name, body.email, body.password)


@public.post("/auth/login")
async def post_login(body: LoginIn) -> dict:
    return identity.login(body.email, body.password)


@public.get("/auth/google/status")
async def google_status() -> dict:
    """Clean OAuth boundary (§27): reports configuration, never fakes auth."""
    from signalcraft.config import settings as _s
    return {"configured": bool(_s.google_client_id and _s.google_client_secret),
            "start_url": "/api/auth/google/start"}


@public.get("/auth/google/start")
async def google_start():
    from fastapi.responses import RedirectResponse

    from signalcraft import oauth as _oauth
    if not _oauth.is_configured():
        from fastapi import HTTPException
        raise HTTPException(status_code=501, detail={
            "code": "oauth_not_configured",
            "message": "Google sign-in needs GOOGLE_CLIENT_ID/SECRET. See docs/development.md.",
        })
    return RedirectResponse(_oauth.start_login(), status_code=302)


@public.get("/auth/google/callback")
async def google_callback(code: str | None = None, state: str | None = None,
                          error: str | None = None):
    from fastapi.responses import RedirectResponse

    from signalcraft import oauth as _oauth
    from signalcraft.config import settings as _s
    front = _s.frontend_url.rstrip("/")
    if error:
        return RedirectResponse(f"{front}/login?error=google_{error}", status_code=302)
    try:
        _, token = _oauth.handle_callback(code or "", state or "")
    except ValueError as e:
        return RedirectResponse(
            f"{front}/login?error={urllib.parse.quote(str(e)[:80])}", status_code=302)
    return RedirectResponse(f"{front}/auth/callback?token={token}", status_code=302)


@router.post("/auth/logout")
async def post_logout(authorization: str | None = Header(default=None)) -> dict:
    token = (authorization or "")[7:] if (authorization or "").lower().startswith("bearer ") else ""
    if not token:
        raise ValueError("missing session token")
    return identity.logout(token)


@router.post("/auth/password")
async def post_password(body: PasswordIn, user_id: int = Depends(get_user_id)) -> dict:
    return identity.password(user_id, body.current, body.new)


@router.get("/auth/me")
async def get_me(user_id: int = Depends(get_user_id)) -> dict:
    return identity.me(user_id)


@router.get("/onboarding/status")
async def get_onboarding_status(user_id: int = Depends(get_user_id)) -> dict:
    return onboarding.status(user_id)


@router.post("/onboarding")
async def post_onboarding(body: OnboardingStep, user_id: int = Depends(get_user_id)) -> dict:
    return onboarding.apply(user_id, **body.model_dump(exclude_none=True))


@router.post("/onboarding/complete")
async def post_onboarding_complete(user_id: int = Depends(get_user_id)) -> dict:
    return onboarding.complete(user_id)


@router.get("/preferences")
async def get_preferences(user_id: int = Depends(get_user_id)) -> dict:
    return preferences.get(user_id)


@router.put("/preferences")
async def put_preferences(body: PreferencesUpdate,
                          user_id: int = Depends(get_user_id)) -> dict:
    return preferences.update(user_id, **body.model_dump(exclude_none=True))


@router.get("/context")
async def get_context(user_id: int = Depends(get_user_id)) -> dict:
    return context.get(user_id)


@router.get("/health")
async def health() -> dict:
    return {"ok": True}


@router.get("/profile", response_model=ProfileOut)
async def get_profile(user_id: int = Depends(get_user_id)) -> dict:
    return profile.get(user_id)


@router.put("/profile", response_model=ProfileOut)
async def put_profile(body: ProfileUpdate, user_id: int = Depends(get_user_id)) -> dict:
    return profile.update(user_id, **body.model_dump())


@router.get("/trends", response_model=list[TrendSignal])
async def get_trends(top_n: int = 10, sort: str = "for_you",
                     user_id: int = Depends(get_user_id)) -> list:
    rows = [
        {k: (t.get(k, 0) if k not in ("topic", "evidence_titles") else t.get(k))
         for k in ("topic", "freshness", "growth", "relevance", "source_momentum",
                   "novelty", "audience_fit", "competition", "trend_score",
                   "evidence_titles")}
        for t in trend.list(user_id, top_n * 2)
    ]
    key = {"rising": "growth", "latest": "freshness"}.get(sort, "trend_score")
    rows.sort(key=lambda t: t[key], reverse=True)
    return rows[:top_n]


@router.get("/opportunities", response_model=list[Opportunity])
async def get_opportunities(limit: int = 20, offset: int = 0, refresh: bool = False,
                            user_id: int = Depends(get_user_id)) -> list:
    if refresh:
        return opportunity.rank(user_id)
    return opportunity.list(user_id, limit, offset)


@router.post("/research")
async def post_research(body: ResearchRun, user_id: int = Depends(get_user_id)) -> dict:
    return research.run(body.query, body.limit, body.use_live, user_id)


@router.get("/research")
async def get_research(query: str = "", limit: int = 30, offset: int = 0,
                       user_id: int = Depends(get_user_id)) -> dict:
    return {"documents": research.documents(user_id, query, limit, offset)}


@router.post("/content/generate")
async def post_generate(body: GenerateIn, user_id: int = Depends(get_user_id)) -> dict:
    return content.generate(body.opportunity_id, body.platform, user_id,
                            tone=body.tone, length=body.length,
                            style_match=body.style_match, grounded=body.grounded,
                            format=body.format)


@router.post("/content/critique")
async def post_critique(body: CritiqueIn) -> dict:
    return content.critique(body.body, body.platform, body.topic)


@router.post("/content/revise")
async def post_revise(body: ReviseIn, user_id: int = Depends(get_user_id)) -> dict:
    return content.revise(body.content_id, user_id)


@router.post("/content/improve-preview")
async def post_improve_preview(body: ImproveIn) -> dict:
    return content.improve_preview(body.body, body.platform)


@router.post("/content/save")
async def post_save(body: SaveIn, user_id: int = Depends(get_user_id)) -> dict:
    """Explicit Save (§13): only this creates a permanent library record."""
    return content.save(user_id, body.opportunity_id, body.platform, body.title,
                        body.body, body.hook, body.cta, body.brief, body.format)


@router.post("/content/{content_id}/restore")
async def post_restore(content_id: int, body: RestoreIn, user_id: int = Depends(get_user_id)) -> dict:
    """Restore a version by copying it forward (history stays append-only)."""
    return content.restore(user_id, content_id, body.version)


@router.put("/opportunities/{opportunity_id}/dismiss")
async def put_dismiss(opportunity_id: int, user_id: int = Depends(get_user_id)) -> dict:
    return opportunity.dismiss(user_id, opportunity_id)


@router.get("/content", response_model=list[ContentItem])
async def get_content(limit: int = 50, offset: int = 0, platform: str | None = None,
                      user_id: int = Depends(get_user_id)) -> list:
    return content.history(user_id, limit, offset, platform)


@router.get("/content/{content_id}", response_model=ContentDetail)
async def get_content_one(content_id: int, user_id: int = Depends(get_user_id)) -> dict:
    return get_content_detail(content_id, user_id)


@router.delete("/content/{content_id}")
async def delete_content(content_id: int, user_id: int = Depends(get_user_id)) -> dict:
    return content.remove(user_id, content_id)


@router.post("/content/{content_id}/duplicate")
async def duplicate_content(content_id: int, user_id: int = Depends(get_user_id)) -> dict:
    return content.duplicate(user_id, content_id)


@router.put("/content/{content_id}/status")
async def put_content_status(content_id: int, body: StatusIn,
                             user_id: int = Depends(get_user_id)) -> dict:
    return content.set_status(content_id, user_id, body.status)


@router.post("/content/{content_id}/performance", response_model=Performance)
async def post_performance(content_id: int, body: PerformanceIn,
                           user_id: int = Depends(get_user_id)) -> dict:
    return content.log_performance(content_id, user_id, **body.model_dump())


@router.get("/analytics")
async def get_analytics(user_id: int = Depends(get_user_id)) -> dict:
    return summary(user_id)


@router.get("/insights")
async def get_insights(user_id: int = Depends(get_user_id)) -> dict:
    return {"insights": insights(user_id)}


@router.post("/agent/chat", response_model=ChatOut)
async def post_chat(body: ChatIn, user_id: int = Depends(get_user_id)) -> dict:
    out = agent.chat(body.message, user_id)
    return {"answer": out["answer"], "intent": out["intent"], "trace": out.get("trace", {}),
            "actions": out.get("actions", []),
            "request_id": out.get("request_id", current_request_id())}


@router.post("/agent/learn")
async def post_learn(user_id: int = Depends(get_user_id)) -> dict:
    return agent.learn(user_id)


@router.get("/agent/memory")
async def get_memory(limit: int = 50, user_id: int = Depends(get_user_id)) -> dict:
    return {"memories": agent.memories(user_id, limit)}


@router.post("/agent/memory")
async def post_memory(body: MemoryIn, user_id: int = Depends(get_user_id)) -> dict:
    return agent.store_memory(user_id, body.kind, body.key, body.value, body.confidence)


@router.get("/calendar")
async def get_calendar(limit: int = 30, user_id: int = Depends(get_user_id)) -> dict:
    return {"items": agent.calendar(user_id, limit)}


@router.post("/calendar")
async def post_calendar(body: ScheduleIn, user_id: int = Depends(get_user_id)) -> dict:
    return agent.schedule(user_id, platform=body.platform,
                          scheduled_for=body.scheduled_for,
                          content_id=body.content_id, notes=body.notes)


@router.put("/calendar/{entry_id}")
async def put_calendar(entry_id: int, body: CalendarUpdate,
                       user_id: int = Depends(get_user_id)) -> dict:
    return agent.reschedule(user_id, entry_id, **body.model_dump(exclude_none=True))


@router.post("/calendar/{entry_id}/duplicate")
async def duplicate_calendar(entry_id: int, user_id: int = Depends(get_user_id)) -> dict:
    return agent.duplicate_entry(user_id, entry_id)


@router.get("/debug/llm")
async def debug_llm() -> dict:
    from signalcraft.db import get_conn
    conn = get_conn()
    try:
        rows = conn.execute(
            "SELECT provider, model, task, COUNT(*) AS calls,"
            " AVG(latency_ms) AS avg_ms, SUM(cost_usd) AS cost,"
            " SUM(CASE WHEN success=0 THEN 1 ELSE 0 END) AS failures"
            " FROM llm_requests GROUP BY provider, model, task"
            " ORDER BY calls DESC LIMIT 50").fetchall()
        return {"usage": [dict(r) for r in rows]}
    finally:
        conn.close()
