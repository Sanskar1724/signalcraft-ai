const API = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

async function req<T>(path: string, init?: RequestInit): Promise<T> {
  const { authHeaders } = await import("./auth");
  const res = await fetch(`${API}${path}`, {
    ...init,
    headers: { "Content-Type": "application/json", ...(await authHeaders()), ...(init?.headers ?? {}) },
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body?.error?.message ?? `API ${res.status}`);
  }
  return res.json() as Promise<T>;
}

export const api = {
  health: () => req<{ ok: boolean }>("/api/health"),
  profile: () => req<Profile>("/api/profile"),
  updateProfile: (p: Partial<Profile>) =>
    req<Profile>("/api/profile", { method: "PUT", body: JSON.stringify(p) }),
  trends: (top_n = 10) => req<TrendSignal[]>(`/api/trends?top_n=${top_n}`),
  opportunities: (refresh = false) =>
    req<Opportunity[]>(`/api/opportunities${refresh ? "?refresh=true" : ""}`),
  runResearch: (limit = 20) =>
    req<{ research: number; trends: number; opportunities: number }>("/api/research", {
      method: "POST",
      body: JSON.stringify({ limit, use_live: true }),
    }),
  generate: (opportunity_id: number, platform: string) =>
    req<GenerateResult>("/api/content/generate", {
      method: "POST",
      body: JSON.stringify({ opportunity_id, platform }),
    }),
  critique: (body: string, platform: string) =>
    req<Critique>("/api/content/critique", {
      method: "POST",
      body: JSON.stringify({ body, platform }),
    }),
  revise: (content_id: number) =>
    req<GenerateResult>("/api/content/revise", {
      method: "POST",
      body: JSON.stringify({ content_id }),
    }),
  library: () => req<ContentItem[]>("/api/content?limit=50"),
  detail: (id: number) => req<ContentDetail>(`/api/content/${id}`),
  logPerformance: (id: number, m: PerformanceInput) =>
    req(`/api/content/${id}/performance`, { method: "POST", body: JSON.stringify(m) }),
  analytics: () => req<AnalyticsSummary>("/api/analytics"),
  insights: () => req<{ insights: string[] }>("/api/insights"),
  chat: (message: string) =>
    req<ChatReply>("/api/agent/chat", { method: "POST", body: JSON.stringify({ message }) }),
  learn: () => req<{ learned: string[] }>("/api/agent/learn", { method: "POST" }),
  memories: () => req<{ memories: Memory[] }>("/api/agent/memory"),
  calendar: () => req<{ items: CalendarItem[] }>("/api/calendar"),
  schedule: (s: { platform: string; scheduled_for: string; content_id?: number; notes: string }) =>
    req("/api/calendar", { method: "POST", body: JSON.stringify(s) }),
  signup: (name: string, email: string, password: string) =>
    req<{ user: { onboarding_status: string }; token: string }>("/api/auth/signup", {
      method: "POST",
      body: JSON.stringify({ name, email, password }),
    }),
  login: (email: string, password: string) =>
    req<{ user: { onboarding_status: string }; token: string }>("/api/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }),
  logout: () => req("/api/auth/logout", { method: "POST" }),
  changePassword: (current: string, next: string) =>
    req("/api/auth/password", { method: "POST", body: JSON.stringify({ current, new: next }) }),  me: () => req<{ user: { name: string; email: string }; onboarding_status: string }>("/api/auth/me"),
  onboardStatus: () => req<{ status: string; name_set: boolean; niche_set: boolean }>("/api/onboarding/status"),
  onboardStep: (step: Record<string, unknown>) =>
    req<{ status: string; name_set: boolean; niche_set: boolean }>("/api/onboarding", {
      method: "POST",
      body: JSON.stringify(step),
    }),
  onboardComplete: () =>
    req<{ status: string; summary: Record<string, unknown>; built: Record<string, number> }>(
      "/api/onboarding/complete",
      { method: "POST" }
    ),
  getPreferences: () => req<Preferences>("/api/preferences"),
  savePreferences: (p: Partial<Preferences>) =>
    req<Preferences>("/api/preferences", { method: "PUT", body: JSON.stringify(p) }),
  context: () => req<Record<string, unknown>>("/api/context"),
};

export interface Profile {
  name: string;
  role: string;
  bio: string;
  location: string;
  niche: string;
  expertise: string;
  expertise_level: string;
  audience: string;
  goals: string;
  platforms: string[];
  writing_style: string;
  tone: string;
  topics: string[];
  avoid_topics: string[];
  style_notes: string;
  content_preferences: string;
  posting_preferences: string;
}

export interface TrendSignal {
  topic: string;
  freshness: number;
  growth: number;
  relevance: number;
  source_momentum: number;
  novelty: number;
  audience_fit: number;
  competition: number;
  trend_score: number;
}

export interface Opportunity {
  id: number;
  topic: string;
  trend_score: number;
  user_relevance: number;
  audience_fit: number;
  freshness: number;
  competition: number;
  why_now: string;
  why_you: string;
  audience: string;
  angle: string;
  format: string;
  platform: string;
  score: number;
  confidence: number;
}

export interface ContentItem {
  id: number;
  platform: string;
  title: string;
  quality_score: number;
  status: string;
  created_at: string;
}

export interface ContentDetail extends ContentItem {
  body: string;
  brief: Record<string, unknown>;
  versions: { version: number; score: number; created_at: string }[];
  performance: Record<string, number>;
}

export interface GenerateResult {
  content: ContentItem & { body: string };
  critique: Critique;
  brief: Record<string, unknown>;
}

export interface Critique {
  overall: number;
  suggestion: string;
  scores: Record<string, number>;
  issues: string[];
}

export interface PerformanceInput {
  platform?: string;
  impressions: number;
  likes: number;
  comments: number;
  shares: number;
  clicks: number;
  saves: number;
  reach: number;
}

export interface AnalyticsSummary {
  posts: number;
  avg_engagement: number;
  best_topics: { topic: string; posts: number; avg_engagement: number }[];
  weak_topics: { topic: string; posts: number; avg_engagement: number }[];
  by_platform: { platform: string; posts: number; avg_engagement: number }[];
  top_content: { id: number; title: string; performance_score: number }[];
  rows: { id: number; title: string; platform: string; engagement_rate: number; performance_score: number }[];
}

export interface ChatReply {
  answer: string;
  intent: string;
  request_id: string;
  trace: { request_id: string; steps: { stage: string; detail?: unknown }[] };
}

export interface Memory {
  kind: string;
  key: string;
  value: string;
  hits: number;
}

export interface CalendarItem {
  scheduled_for: string;
  platform: string;
  status: string;
  title?: string | null;
  notes: string;
}

export interface Preferences {
  tone: string;
  length: string;
  creativity: number;
  research_depth: string;
  use_trends: number;
  always_research: number;
  citation_pref: string;
  emoji_pref: string;
  cta_pref: string;
  formality: string;
  sentence_style: string;
  formats: string[];
  frequency: string;
}
