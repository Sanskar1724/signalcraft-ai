"use client";

import Link from "next/link";
import { useEffect, useState, type ReactNode } from "react";
import { useRouter } from "next/navigation";
import Logo from "../../components/Logo";
import Status from "../../components/Status";
import { clearToken, getToken } from "../../lib/auth";
import { api } from "../../lib/api";

const NAV: [string, string][] = [
  ["Overview", "/app"],
  ["Trends", "/app/trends"],
  ["Opportunities", "/app/opportunities"],
  ["Create", "/app/create"],
  ["Library", "/app/library"],
  ["Analytics", "/app/analytics"],
  ["Calendar", "/app/calendar"],
  ["Agent", "/app/agent"],
  ["Settings", "/app/settings/profile"],
];

const MOBILE: [string, string][] = [
  ["Home", "/app"],
  ["Trends", "/app/trends"],
  ["Create", "/app/create"],
  ["Library", "/app/library"],
  ["Agent", "/app/agent"],
];

export default function AppShell({ children }: { children: ReactNode }) {
  const router = useRouter();
  const [name, setName] = useState("");
  const [ready, setReady] = useState(false);

  useEffect(() => {
    if (!getToken()) {
      router.replace("/login");
      return;
    }
    api.me()
      .then((me) => {
        if (me.onboarding_status !== "COMPLETED") router.replace("/onboarding");
        else {
          setName(me.user.name);
          setReady(true);
        }
      })
      .catch(() => {
        clearToken();
        router.replace("/login");
      });
  }, [router]);

  if (!ready) return <main className="main"><p className="muted">Loading your workspace…</p></main>;

  return (
    <div className="shell">
      <aside className="side">
        <div className="brandrow">
          <Logo />
          <div className="brandname">Signal<span>Craft</span></div>
        </div>
        <p className="tag">{name ? `for ${name}` : "Your personal AI content strategist."}</p>
        <nav>
          {NAV.map(([label, href]) => (
            <Link key={href} href={href} className="navlink">
              <span className="navdot" />
              {label}
            </Link>
          ))}
        </nav>
        <div className="sidefoot">
          <Status /> · v0.1
          <p style={{ margin: "8px 0 0" }}>
            <button
              className="btn ghost small"
              onClick={() => {
                api.logout().finally(() => {
                  clearToken();
                  router.replace("/login");
                });
              }}
            >
              Log out
            </button>
          </p>
        </div>
      </aside>
      <main className="main">{children}</main>
      <nav className="mobilenav">
        {MOBILE.map(([label, href]) => (
          <Link key={href} href={href}>{label}</Link>
        ))}
      </nav>
    </div>
  );
}
