"""Pydantic read models mirroring the §6 entities."""
from __future__ import annotations

from pydantic import BaseModel


class ProfileOut(BaseModel):
    user_id: int = 1
    niche: str = ""
    expertise: str = ""
    expertise_level: str = ""
    audience: str = ""
    goals: str = ""
    platforms: list[str] = []
    writing_style: str = ""
    tone: str = ""
    topics: list[str] = []
    avoid_topics: list[str] = []
    style_notes: str = ""
    content_preferences: str = ""
    posting_preferences: str = ""


class TrendSignal(BaseModel):
    topic: str
    freshness: float = 0
    growth: float = 0
    relevance: float = 0
    source_momentum: float = 0
    novelty: float = 0
    audience_fit: float = 0
    competition: float = 0
    trend_score: float = 0


class Opportunity(BaseModel):
    id: int
    topic: str
    trend_score: float = 0
    user_relevance: float = 0
    audience_fit: float = 0
    freshness: float = 0
    competition: float = 0
    why_now: str = ""
    why_you: str = ""
    audience: str = ""
    angle: str = ""
    format: str = ""
    platform: str = ""
    score: float = 0
    confidence: float = 0


class ContentItem(BaseModel):
    id: int
    platform: str = ""
    title: str = ""
    hook: str = ""
    cta: str = ""
    quality_score: float = 0
    status: str = "draft"
    created_at: str = ""


class ContentVersion(BaseModel):
    version: int
    score: float = 0
    created_at: str = ""


class ContentDetail(ContentItem):
    body: str = ""
    brief: dict = {}
    versions: list[ContentVersion] = []
    performance: dict = {}
    opportunity_topic: str | None = None


class Performance(BaseModel):
    content_id: int
    platform: str = ""
    impressions: int = 0
    likes: int = 0
    comments: int = 0
    shares: int = 0
    clicks: int = 0
    saves: int = 0
    reach: int = 0
    engagement_rate: float = 0
    performance_score: float = 0


class Memory(BaseModel):
    kind: str
    key: str
    value: str = ""
    confidence: float = 0.5
    hits: int = 1


class ChatOut(BaseModel):
    answer: str
    intent: str
    request_id: str = ""
    trace: dict = {}
