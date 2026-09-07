"""Typed stage contracts (§4): every pipeline stage validates its input.

Raw parser output never crosses a stage boundary unvalidated. LLM-related
outputs reuse llm/schemas.py; these cover research → trends → opportunities
→ content → performance → insights → memory → agent.
"""
from __future__ import annotations

from pydantic import BaseModel, Field

from .llm.schemas import ContentBrief, CritiqueScores  # noqa: F401 (re-export)

__all__ = ["ResearchDocument", "TrendSignal", "Opportunity", "GeneratedContent",
           "PerformanceMetric", "Insight", "CreatorMemory", "AgentResult",
           "ContentBrief", "CritiqueScores"]


class ResearchDocument(BaseModel):
    source: str = "unknown"
    source_type: str = "rss"
    source_url: str = ""
    title: str = Field(min_length=1, max_length=300)
    summary: str = ""
    keywords: list[str] = Field(default_factory=list)
    topic: str = ""
    published_at: str = ""
    retrieved_at: str = ""
    relevance: float = Field(default=0.0, ge=0.0, le=1.0)
    freshness: float = Field(default=0.0, ge=0.0, le=1.0)


class TrendSignal(BaseModel):
    topic: str = Field(min_length=1)
    freshness: float = 0
    growth: float = 0
    relevance: float = 0
    source_momentum: float = 0
    novelty: float = 0
    audience_fit: float = 0
    competition: float = 0
    trend_score: float = 0
    evidence: list[int] = Field(default_factory=list)
    evidence_titles: list[str] = Field(default_factory=list)


class Opportunity(BaseModel):
    topic: str = Field(min_length=1)
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
    research_refs: list[int] = Field(default_factory=list)


class GeneratedContent(BaseModel):
    platform: str = ""
    title: str = ""
    body: str = Field(min_length=40)
    hook: str = ""
    cta: str = ""
    quality_score: float = 0
    brief: dict = Field(default_factory=dict)


class PerformanceMetric(BaseModel):
    content_id: int
    platform: str = ""
    impressions: int = Field(default=0, ge=0)
    likes: int = Field(default=0, ge=0)
    comments: int = Field(default=0, ge=0)
    shares: int = Field(default=0, ge=0)
    clicks: int = Field(default=0, ge=0)
    saves: int = Field(default=0, ge=0)
    reach: int = Field(default=0, ge=0)
    engagement_rate: float = 0
    performance_score: float = 0


class Insight(BaseModel):
    text: str = Field(min_length=1)
    kind: str = "observation"  # observation | recommendation | warning


class CreatorMemory(BaseModel):
    kind: str = Field(min_length=1)
    key: str = Field(min_length=1, max_length=120)
    value: str = ""
    confidence: float = Field(default=0.6, ge=0.0, le=1.0)


class AgentResult(BaseModel):
    answer: str = Field(min_length=1)
    intent: str = "general"
    request_id: str = ""
    trace: dict = Field(default_factory=dict)
