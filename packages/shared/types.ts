/** Shared API contracts (mirrors apps/api models). Frontend + docs reference these. */
export interface TrendSignal {
  topic: string;
  trend_score: number;
  audience_fit: number;
  competition: number;
}

export interface Opportunity {
  id: number;
  topic: string;
  trend_score: number;
  score: number;
  confidence: number;
  platform: string;
}
