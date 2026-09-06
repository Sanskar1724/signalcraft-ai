export default function Logo({ size = 34 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 40 40" aria-label="SignalCraft logo">
      <defs>
        <linearGradient id="sc-g" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0" stopColor="#2dd4bf" />
          <stop offset="1" stopColor="#0ea5a4" />
        </linearGradient>
      </defs>
      <rect x="1" y="1" width="38" height="38" rx="11" fill="url(#sc-g)" opacity="0.92" />
      <path
        d="M7 24 L13 24 L16 14 L20 30 L24 19 L26 24 L33 24"
        fill="none"
        stroke="#042a26"
        strokeWidth="2.6"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <circle cx="26" cy="24" r="2.4" fill="#042a26" />
    </svg>
  );
}
