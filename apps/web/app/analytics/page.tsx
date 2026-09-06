"use client";

import { useEffect, useState } from "react";
import { api, type AnalyticsSummary } from "../../lib/api";

export default function AnalyticsPage() {
  const [data, setData] = useState<AnalyticsSummary | null>(null);

  useEffect(() => {
    api.analytics().then(setData).catch(() => setData(null));
  }, []);

  if (!data) return <p>Loading…</p>;

  return (
    <>
      <h1>Performance</h1>
      <div className="grid3">
        <div className="metric"><b>{data.posts}</b>Posts</div>
        <div className="metric"><b>{data.avg_engagement}%</b>Avg engagement</div>
      </div>
      <h2>Best topics</h2>
      {data.best_topics.map((t) => (
        <p key={t.topic}>{t.topic} — {t.avg_engagement}% ({t.posts})</p>
      ))}
      <h2>Weak topics</h2>
      {data.weak_topics.map((t) => (
        <p key={t.topic}>{t.topic} — {t.avg_engagement}% ({t.posts})</p>
      ))}
      <h2>Best formats</h2>
      {data.by_platform.map((t) => (
        <p key={t.platform}>{t.platform} — {t.avg_engagement}% ({t.posts})</p>
      ))}
    </>
  );
}
