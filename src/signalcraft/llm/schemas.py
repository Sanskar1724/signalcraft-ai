"""Pydantic schemas for LLM structured outputs (§22: validate, never blindly trust)."""
from __future__ import annotations

from pydantic import BaseModel, Field


class TopicClassification(BaseModel):
    label: str = "unknown"
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)


class TrendVerdict(BaseModel):
    emerging: bool = False
    reason: str = ""


class CritiqueScores(BaseModel):
    relevance: float = Field(default=5.0, ge=0.0, le=10.0)
    clarity: float = Field(default=5.0, ge=0.0, le=10.0)
    originality: float = Field(default=5.0, ge=0.0, le=10.0)
    hook: float = Field(default=5.0, ge=0.0, le=10.0)
    readability: float = Field(default=5.0, ge=0.0, le=10.0)
    platform_fit: float = Field(default=5.0, ge=0.0, le=10.0)
    evidence: float = Field(default=5.0, ge=0.0, le=10.0)
    tone: float = Field(default=5.0, ge=0.0, le=10.0)
    cta: float = Field(default=5.0, ge=0.0, le=10.0)
    issues: list[str] = Field(default_factory=list)
    suggestion: str = ""


class ContentBrief(BaseModel):
    """Structured content brief (§13) — the LLM generates FROM this."""

    topic: str
    target_audience: str = ""
    objective: str = "Engage and inform"
    platform: str = "LinkedIn"
    core_message: str = ""
    angle: str = ""
    hook_strategy: str = "One sharp, specific opening line"
    supporting_evidence: list[str] = Field(default_factory=list)
    cta: str = ""
    tone: str = ""
    things_to_avoid: list[str] = Field(default_factory=list)
