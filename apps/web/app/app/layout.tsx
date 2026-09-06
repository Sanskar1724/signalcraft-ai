"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState, type ReactNode } from "react";
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

const CRUMBS: Record<string, string> = {
  "/app": "Overview",
  "/app/trends": "Trends",
  "/app/opportunities": "Opportunities",
  "/app/create": "Create",
  "/app/library": "Library",
  "/app/analytics": "Analytics",
  "/app/calendar": "Calendar",
  "/app/agent": "Agent",
  "/app/settings/profile": "Settings · Profile",
  "/app/settings/preferences": "Settings · Preferences",
  "/app/settings/account": "Settings · Account",
};

export default function AppShell({ children }: { children: ReactNode }) {
  const router = useRouter();
  const path = usePathname();
  const [name, setName] = useState("");
  const [ready, setReady] = useState(false);
  const [collapsed, setCollapsed] = useState(false);
  const [menu, setMenu] = useState(false);

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

  function logout() {
    api.logout().finally(() => {
      clearToken();
      router.replace("/login");
    });
  }

  if (!ready) return <main className="main"><p className="muted">Loading your workspace…</p></main>;

  return (
    <div className="shell">
      <aside className={"side" + (collapsed ? " collapsed" : "")}>
        <div className="brandrow">
          <Logo />
          <div className="brandname">Signal<span>Craft</span></div>
        </div>
        <p className="tag">{name ? `for ${name}` : "Your personal AI content strategist."}</p>
        <nav aria-label="Application">
          {NAV.map(([label, href]) => (
            <Link key={href} href={href} className={"navlink" + (path === href ? " active" : "")}>
              <span className="navdot" />
              <span className="navlabel">{label}</span>
            </Link>
          ))}
        </nav>
        <div className="sidefoot">
          <Status /> · v0.1
        </div>
      </aside>
      <div style={{ flex: 1, minWidth: 0 }}>
        <header className="topbar">
          <button className="iconbtn" aria-label="Toggle sidebar" onClick={() => setCollapsed(!collapsed)}>
            ☰
          </button>
          <span className="crumbs">SignalCraft / {CRUMBS[path] ?? "Workspace"}</span>
          <Status />
          <div style={{ position: "relative" }}>
            <button className="avatar" aria-label="Profile menu" onClick={() => setMenu(!menu)}>
              {(name || "?").trim().charAt(0).toUpperCase()}
            </button>
            {menu && (
              <div className="menu" role="menu">
                <Link href="/app/settings/profile" onClick={() => setMenu(false)}>Profile settings</Link>
                <Link href="/app/settings/account" onClick={() => setMenu(false)}>Account</Link>
                <button onClick={logout}>Log out</button>
              </div>
            )}
          </div>
        </header>
        <main className="main">{children}</main>
      </div>
      <nav className="mobilenav" aria-label="Mobile">
        {MOBILE.map(([label, href]) => (
          <Link key={href} href={href}>{label}</Link>
        ))}
      </nav>
    </div>
  );
}
