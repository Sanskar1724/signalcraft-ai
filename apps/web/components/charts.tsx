"use client";

export function Sparkline({ points, w = 280, h = 72 }: { points: number[]; w?: number; h?: number }) {
  if (points.length < 2) return <p className="muted">Not enough data yet.</p>;
  const max = Math.max(...points, 1);
  const min = Math.min(...points, 0);
  const span = max - min || 1;
  const step = w / (points.length - 1);
  const xy = points.map((p, i) => [i * step, h - 6 - ((p - min) / span) * (h - 14)] as const);
  const line = xy.map(([x, y], i) => `${i ? "L" : "M"}${x.toFixed(1)},${y.toFixed(1)}`).join(" ");
  const area = `${line} L${w},${h} L0,${h} Z`;
  const id = `g${points.length}-${Math.round(max * 10)}`;
  return (
    <svg width="100%" viewBox={`0 0 ${w} ${h}`} preserveAspectRatio="none" style={{ height: h }}>
      <defs>
        <linearGradient id={id} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor="#6366f1" stopOpacity="0.45" />
          <stop offset="1" stopColor="#6366f1" stopOpacity="0.02" />
        </linearGradient>
      </defs>
      <path d={area} fill={`url(#${id})`} />
      <path d={line} fill="none" stroke="#22d3ee" strokeWidth="2" strokeLinejoin="round" />
      {xy.map(([x, y], i) => (
        <circle key={i} cx={x} cy={y} r="2.4" fill="#0a0f1e" stroke="#22d3ee" strokeWidth="1.4" />
      ))}
    </svg>
  );
}

export function HBar({ label, value, max, suffix = "%" }: { label: string; value: number; max: number; suffix?: string }) {
  return (
    <div style={{ margin: "8px 0" }}>
      <div className="row" style={{ alignItems: "center" }}>
        <span style={{ flex: 1, fontSize: 13 }}>{label}</span>
        <b style={{ fontSize: 13 }}>{value}{suffix}</b>
      </div>
      <div className="bar"><i style={{ width: `${Math.max(2, Math.min(100, (value / Math.max(max, 0.01)) * 100))}%` }} /></div>
    </div>
  );
}

export function timeAgo(iso: string): string {
  const t = new Date(iso.replace(" ", "T") + "Z").getTime();
  if (Number.isNaN(t)) return iso;
  const s = Math.max(0, (Date.now() - t) / 1000);
  if (s < 90) return "just now";
  const m = Math.floor(s / 60);
  if (m < 90) return `${m}m ago`;
  const h = Math.floor(m / 60);
  if (h < 48) return `${h}h ago`;
  return `${Math.floor(h / 24)}d ago`;
}
