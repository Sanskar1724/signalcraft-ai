import Link from "next/link";
import type { ReactNode } from "react";
import Logo from "../components/Logo";
import Status from "../components/Status";
import "./globals.css";

const NAV: [string, string][] = [
  ["Overview", "/"],
  ["Trending For You", "/trending"],
  ["Content Opportunities", "/opportunities"],
  ["Create", "/create"],
  ["Content Library", "/library"],
  ["Analytics", "/analytics"],
  ["Content Calendar", "/calendar"],
  ["AI Insights", "/insights"],
  ["Agent", "/agent"],
  ["Settings", "/settings"],
];

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>
        <div className="shell">
          <aside className="side">
            <div className="brandrow">
              <Logo />
              <div className="brandname">
                Signal<span>Craft</span>
              </div>
            </div>
            <p className="tag">Your personal AI content strategist.</p>
            <nav>
              {NAV.map(([label, href]) => (
                <Link key={href} href={href} className="navlink">
                  <span className="navdot" />
                  {label}
                </Link>
              ))}
            </nav>
            <div className="sidefoot"><Status /> · v0.1 · local MVP</div>
          </aside>
          <main className="main">{children}</main>
        </div>
      </body>
    </html>
  );
}
