import Link from "next/link";
import type { ReactNode } from "react";
import "./globals.css";

const NAV = [
  ["Overview", "/"],
  ["Trending For You", "/trending"],
  ["Content Opportunities", "/opportunities"],
  ["Create", "/create"],
  ["Content Library", "/library"],
  ["Analytics", "/analytics"],
  ["Content Calendar", "/calendar"],
  ["AI Insights", "/insights"],
  ["Agent", "/agent"],
];

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>
        <div className="shell">
          <aside className="side">
            <div className="brand">◉ SignalCraft AI</div>
            <p className="tag">Your personal AI content strategist.</p>
            <nav>
              {NAV.map(([label, href]) => (
                <Link key={href} href={href} className="navlink">
                  {label}
                </Link>
              ))}
            </nav>
          </aside>
          <main className="main">{children}</main>
        </div>
      </body>
    </html>
  );
}
