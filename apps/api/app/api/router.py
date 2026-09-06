"""REST routes (§23). All errors use the envelope from core.errors."""
from __future__ import annotations

from fastapi import APIRouter, Depends

from ..analytics.service import insights, summary
from ..api.deps import current_request_id, get_user_id, require_key
from ..core.config import API_PREFIX
from ..models.models import (ChatOut, ContentDetail, ContentItem, Opportunity,
                             Performance, ProfileOut, TrendSignal)
from ..repositories.content import get_content_detail
from ..schemas.schemas import (ChatIn, CritiqueIn, GenerateIn, PerformanceIn,
                               ProfileUpdate, ResearchRun, ReviseIn, ScheduleIn)
from ..services.services import agent, content, opportunity, profile, research, trend

router = APIRouter(prefix=API_PREFIX, dependencies=[Depends(require_key)])


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
async def get_trends(top_n: int = 10, user_id: int = Depends(get_user_id)) -> list:
    return [
        {k: t.get(k, 0) if k != "topic" else t["topic"]
         for k in ("topic", "freshness", "growth", "relevance", "source_momentum",
                   "novelty", "audience_fit", "competition", "trend_score")}
        for t in trend.list(user_id, top_n)
    ]


@router.get("/opportunities", response_model=list[Opportunity])
async def get_opportunities(limit: int = 20, offset: int = 0, refresh: bool = False,
                            user_id: int = Depends(get_user_id)) -> list:
    if refresh:
        return opportunity.rank(user_id)
    return opportunity.list(user_id, limit, offset)


@router.post("/research")
async def post_research(body: ResearchRun, user_id: int = Depends(get_user_id)) -> dict:
    return research.run(body.query, body.limit, body.use_live, user_id)


@router.post("/content/generate")
async def post_generate(body: GenerateIn, user_id: int = Depends(get_user_id)) -> dict:
    return content.generate(body.opportunity_id, body.platform, user_id)


@router.post("/content/critique")
async def post_critique(body: CritiqueIn) -> dict:
    return content.critique(body.body, body.platform, body.topic)


@router.post("/content/revise")
async def post_revise(body: ReviseIn, user_id: int = Depends(get_user_id)) -> dict:
    return content.revise(body.content_id, user_id)


@router.get("/content", response_model=list[ContentItem])
async def get_content(limit: int = 50, offset: int = 0, platform: str | None = None,
                      user_id: int = Depends(get_user_id)) -> list:
    return content.history(user_id, limit, offset, platform)


@router.get("/content/{content_id}", response_model=ContentDetail)
async def get_content_one(content_id: int, user_id: int = Depends(get_user_id)) -> dict:
    return get_content_detail(content_id, user_id)


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
            "request_id": out.get("request_id", current_request_id())}


@router.post("/agent/learn")
async def post_learn(user_id: int = Depends(get_user_id)) -> dict:
    return agent.learn(user_id)


@router.get("/agent/memory")
async def get_memory(limit: int = 50, user_id: int = Depends(get_user_id)) -> dict:
    return {"memories": agent.memories(user_id, limit)}


@router.get("/calendar")
async def get_calendar(limit: int = 30, user_id: int = Depends(get_user_id)) -> dict:
    return {"items": agent.calendar(user_id, limit)}


@router.post("/calendar")
async def post_calendar(body: ScheduleIn, user_id: int = Depends(get_user_id)) -> dict:
    return agent.schedule(user_id, platform=body.platform,
                          scheduled_for=body.scheduled_for,
                          content_id=body.content_id, notes=body.notes)


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
