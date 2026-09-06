const API = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

async function req<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API}${path}`, {
    ...init,
    headers: { "Content-Type": "application/json", ...(init?.headers ?? {}) },
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
  memories: () => req<{ memories: Memory[] }>("/api/agent/memory"),
  calendar: () => req<{ items: CalendarItem[] }>("/api/calendar"),
};

export interface Profile {
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
  versions: { version: number; score: number }[];
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
}

export interface ChatReply {
  answer: string;
  intent: string;
  request_id: string;
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
