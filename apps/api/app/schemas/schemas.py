"""Pydantic request bodies (§23, validated at the boundary)."""
from __future__ import annotations

from pydantic import BaseModel, Field


class ProfileUpdate(BaseModel):
    name: str | None = None
    niche: str | None = None
    expertise: str | None = None
    expertise_level: str | None = None
    audience: str | None = None
    goals: str | None = None
    platforms: list[str] | None = None
    writing_style: str | None = None
    tone: str | None = None
    topics: list[str] | None = None
    avoid_topics: list[str] | None = None
    style_notes: str | None = None
    content_preferences: str | None = None
    posting_preferences: str | None = None
    role: str | None = None
    bio: str | None = None
    location: str | None = None


class ResearchRun(BaseModel):
    query: str = ""
    limit: int = Field(default=20, ge=1, le=100)
    use_live: bool = True


class GenerateIn(BaseModel):
    opportunity_id: int
    platform: str = "LinkedIn"
    tone: str | None = None
    length: str = "medium"


class CritiqueIn(BaseModel):
    body: str = Field(min_length=1, max_length=6000)
    platform: str = "LinkedIn"
    topic: str = ""


class ReviseIn(BaseModel):
    content_id: int


class StatusIn(BaseModel):
    status: str = "draft"


class PerformanceIn(BaseModel):
    platform: str = ""
    impressions: int = Field(default=0, ge=0)
    likes: int = Field(default=0, ge=0)
    comments: int = Field(default=0, ge=0)
    shares: int = Field(default=0, ge=0)
    clicks: int = Field(default=0, ge=0)
    saves: int = Field(default=0, ge=0)
    reach: int = Field(default=0, ge=0)


class ChatIn(BaseModel):
    message: str = Field(min_length=1, max_length=2000)


class ScheduleIn(BaseModel):
    platform: str = "LinkedIn"
    scheduled_for: str = "2026-09-10 10:00"
    content_id: int | None = None
    notes: str = ""


class SignupIn(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    email: str = Field(min_length=3, max_length=200)
    password: str = Field(min_length=8, max_length=200)


class LoginIn(BaseModel):
    email: str = ""
    password: str = ""


class PasswordIn(BaseModel):
    current: str = ""
    new: str = Field(min_length=8, max_length=200)


class OnboardingStep(BaseModel):
    """Any subset of wizard fields (§11); unknown keys are rejected with 422."""

    model_config = {"extra": "forbid"}

    name: str | None = None
    role: str | None = None
    bio: str | None = None
    location: str | None = None
    niche: str | None = None
    secondary_topics: list[str] | None = None
    expertise_level: str | None = None
    audience: str | None = None
    audience_segments: list[str] | None = None
    goals: list[str] | None = None
    platforms: list[str] | None = None
    writing_style: str | None = None
    tone: str | None = None
    topics: list[str] | None = None
    avoid_topics: list[str] | None = None
    avoid_topics_extra: list[str] | None = None
    style_notes: str | None = None
    content_preferences: str | None = None
    posting_preferences: str | None = None
    formats: list[str] | None = None
    frequency: str | None = None
    length: str | None = None
    creativity: float | None = None
    research_depth: str | None = None
    use_trends: bool | None = None
    always_research: bool | None = None
    citation_pref: str | None = None
    emoji_pref: str | None = None
    cta_pref: str | None = None
    formality: str | None = None
    sentence_style: str | None = None


class PreferencesUpdate(BaseModel):
    tone: str | None = None
    length: str | None = None
    creativity: float | None = None
    research_depth: str | None = None
    use_trends: bool | None = None
    always_research: bool | None = None
    citation_pref: str | None = None
    emoji_pref: str | None = None
    cta_pref: str | None = None
    formality: str | None = None
    sentence_style: str | None = None
    formats: list[str] | None = None
    frequency: str | None = None
