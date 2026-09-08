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

export function ScoreRing({ value, size = 92 }: { value: number; size?: number }) {
  const r = 40;
  const c = 2 * Math.PI * r;
  const pct = Math.max(0, Math.min(100, value)) / 100;
  return (
    <svg width={size} height={size} viewBox="0 0 100 100" role="img" aria-label={`score ${value}`}>
      <circle cx="50" cy="50" r={r} fill="none" stroke="rgba(255,255,255,.1)" strokeWidth="10" />
      <circle cx="50" cy="50" r={r} fill="none" stroke="#2dd4bf" strokeWidth="10"
        strokeLinecap="round" strokeDasharray={`${(c * pct).toFixed(1)} ${c.toFixed(1)}`}
        transform="rotate(-90 50 50)" style={{ transition: "stroke-dasharray .8s ease" }} />
      <text x="50" y="56" textAnchor="middle" fill="#f2f4f7" fontSize="20" fontWeight="800">{value}</text>
    </svg>
  );
}

export function Donut({ parts }: { parts: { label: string; value: number }[] }) {
  const total = parts.reduce((a, p) => a + p.value, 0) || 1;
  const colors = ["#2dd4bf", "#7dd3fc", "#a7f3d0", "#fbbf24", "#f87171", "#9aa3b2"];
  const r = 40;
  const c = 2 * Math.PI * r;
  let acc = 0;
  return (
    <div className="row" style={{ alignItems: "center" }}>
      <svg width="120" height="120" viewBox="0 0 100 100" role="img" aria-label="distribution">
        {parts.map((p, i) => {
          const frac = p.value / total;
          const el = (
            <circle key={p.label} cx="50" cy="50" r={r} fill="none"
              stroke={colors[i % colors.length]} strokeWidth="12"
              strokeDasharray={`${(c * frac).toFixed(1)} ${c.toFixed(1)}`}
              strokeDashoffset={(-c * acc).toFixed(1)}
              transform="rotate(-90 50 50)" />
          );
          acc += frac;
          return el;
        })}
      </svg>
      <div>
        {parts.map((p, i) => (
          <p key={p.label} className="muted" style={{ margin: "4px 0", fontSize: 13 }}>
            <span style={{ color: colors[i % colors.length] }}>●</span> {p.label} — {p.value}
          </p>
        ))}
      </div>
    </div>
  );
}

export function timeAgo(iso: string): string {  const t = new Date(iso.replace(" ", "T") + "Z").getTime();
  if (Number.isNaN(t)) return iso;
  const s = Math.max(0, (Date.now() - t) / 1000);
  if (s < 90) return "just now";
  const m = Math.floor(s / 60);
  if (m < 90) return `${m}m ago`;
  const h = Math.floor(m / 60);
  if (h < 48) return `${h}h ago`;
  return `${Math.floor(h / 24)}d ago`;
}
