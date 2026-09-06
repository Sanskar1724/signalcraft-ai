"use client";

import Link from "next/link";
import React, { useEffect, useRef, useState } from "react";
import Logo from "../components/Logo";
import { GitHubIcon } from "../components/Navbar";
import Navbar from "../components/Navbar";
import SignalField from "../components/SignalField";
import { Reveal } from "../components/fx";
import { api } from "../lib/api";

function Section({ id, kicker, title, children }: { id: string; kicker: string; title: string; children: React.ReactNode }) {
  return (
    <section id={id} className="landsec">
      <Reveal>
        <p className="kicker">{kicker}</p>
        <h2 className="landh">{title}</h2>
      </Reveal>
      <Reveal delay={120}>{children}</Reveal>
    </section>
  );
}

function useCountUp(target: number, run: boolean, ms = 1200) {
  const [n, setN] = useState(0);
  useEffect(() => {
    if (!run) return;
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
      setN(target);
      return;
    }
    let raf = 0;
    const t0 = performance.now();
    const step = (t: number) => {
      const p = Math.min(1, (t - t0) / ms);
      setN(Math.round(target * (1 - Math.pow(1 - p, 3))));
      if (p < 1) raf = requestAnimationFrame(step);
    };
    raf = requestAnimationFrame(step);
    return () => cancelAnimationFrame(raf);
  }, [run, target, ms]);
  return n;
}

function useInView<T extends HTMLElement>() {
  const ref = useRef<T>(null);
  const [inView, setInView] = useState(false);
  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const io = new IntersectionObserver(([e]) => {
      if (e.isIntersecting) {
        setInView(true);
        io.disconnect();
      }
    }, { threshold: 0.3 });
    io.observe(el);
    return () => io.disconnect();
  }, []);
  return { ref, inView };
}

function MetricBand() {
  const { ref, inView } = useInView<HTMLDivElement>();
  const a = useCountUp(93, inView);
  const b = useCountUp(7, inView);
  const c = useCountUp(24, inView);
  return (
    <div className="grid3" ref={ref}>
      <div className="metric hot"><b>{a}</b><span>avg opportunity score</span></div>
      <div className="metric"><b>{b}</b><span>signals tracked daily</span></div>
      <div className="metric"><b>+{c}%</b><span>typical engagement lift</span></div>
    </div>
  );
}

function LiveTicker() {
  const [topics, setTopics] = useState<string[]>([]);
  useEffect(() => {
    api.trends(8).then((t) => setTopics(t.map((x) => x.topic))).catch(() => setTopics([]));
  }, []);
  if (!topics.length) return null;
  const row = [...topics, ...topics];
  return (
    <div className="ticker" aria-label="Live trends">
      <div className="tickerin">
        {row.map((t, i) => (
          <span key={i} className="pill">▲ {t}</span>
        ))}
      </div>
    </div>
  );
}

const PLAT_EXAMPLES: Record<string, string> = {
  LinkedIn:
    "AI agents in data pipelines: what changed.\n\nTeams now scaffold ETL with tool-calling agents — with human review gates.\n\nTakeaway: automate the boilerplate, keep the judgment.",
  X: "1/ AI agents in data pipelines: automate the boring parts, review the rest.\n\n2/ Tool-calling agents now scaffold ETL reliably.\n\n3/ Try it on one backfill this week.",
  Blog: "# AI Agents in Data Pipelines\n\nWhy now, how it works, and one experiment to run this week.",
};

function PlatformTabs() {
  const [tab, setTab] = useState("LinkedIn");
  return (
    <div className="card">
      <div className="row">
        {Object.keys(PLAT_EXAMPLES).map((p) => (
          <button key={p} className={p === tab ? "btn small" : "btn ghost small"} onClick={() => setTab(p)}>
            {p}
          </button>
        ))}
      </div>
      <pre className="draft">{PLAT_EXAMPLES[tab]}</pre>
    </div>
  );
}

export default function Landing() {
  return (
    <div className="land">
      <SignalField />
      <Navbar />

      <section className="hero">
        <p className="kicker">Research what matters · Create what resonates · Learn what works</p>
        <h1>Your personal AI<br />content strategist.</h1>
        <p className="lede">
          SignalCraft understands your audience, tracks what is happening right now, finds your
          best content opportunities, and turns them into content that sounds like you.
        </p>
        <div className="row">
          <Link href="/signup" className="btn">Start Creating</Link>
          <a href="https://github.com/Sanskar1724/signalcraft-ai" target="_blank" rel="noreferrer" className="btn ghost">
            Explore GitHub
          </a>
        </div>
        <LiveTicker />

        <div className="heroviz">
          <div className="floatcard">
            <p className="lbl">SignalCraft · Good morning, Sankiyy</p>
            <p className="lbl" style={{ marginTop: 10 }}>Trending for you</p>
            <h3>AI Agents + Data Engineering — <span style={{ color: "var(--accent)" }}>93</span></h3>
            <div className="score"><span>Trend</span><b>94</b></div>
            <div className="score"><span>Audience Fit</span><b>97</b></div>
            <div className="score"><span>Freshness</span><b>96</b></div>
            <p className="muted">“How AI agents are changing data pipeline development.”</p>
            <Link href="/signup" className="btn small">Generate Content</Link>
          </div>
        </div>
      </section>

      <Section id="product" kicker="The problem" title="Most AI writing tools start with a blank box.">
        <div className="grid2">
          <div className="card">
            <p className="lbl">Generic path</p>
            <p className="muted">Prompt → generic output → no strategy → no learning.</p>
          </div>
          <div className="card glow">
            <p className="lbl">SignalCraft path</p>
            <p>You + audience + live trends + your performance = <b>personal intelligence</b>.</p>
          </div>
        </div>
      </Section>

      <Section id="how" kicker="How it works" title="Five steps, one loop.">
        <MetricBand />
        <div style={{ marginTop: 18 }}>
          {[
            ["01", "Understand You", "Niche, audience, goals, style — captured once, used everywhere."],
            ["02", "Track the World", "Fresh research, deduplicated and scored for you."],
            ["03", "Find Your Opportunity", "Ranked topics, each with its reason."],
            ["04", "Create Native Drafts", "Brief-led LinkedIn, X and Blog output with critique."],
            ["05", "Learn What Works", "Performance becomes memory that re-ranks everything."],
          ].map(([n, t, d]) => (
            <div className="howstep" key={n}>
              <span className="num">{n}</span>
              <div><h3>{t}</h3><p className="muted">{d}</p></div>
            </div>
          ))}
        </div>
      </Section>

      <Section id="intelligence" kicker="Live demo" title="Try the voices, then make them yours.">
        <PlatformTabs />
      </Section>

      <Section id="agent" kicker="AI agent" title="Just ask. It knows your data.">
        <div className="agentmock">
          <div className="q"><b>You:</b> What should I post today?</div>
          <div className="a">Three opportunities fit your audience. Strongest: AI agents in data engineering (91/100).</div>
          <div className="q"><b>You:</b> Turn it into an X thread.</div>
          <div className="a">Done — check Create.</div>
        </div>
      </Section>

      <section className="landsec center">
        <Reveal>
          <h2 className="landh">Stop guessing what to post.</h2>
          <p className="lede">Two-minute setup. Your first briefing today.</p>
          <div className="row" style={{ justifyContent: "center" }}>
            <Link href="/signup" className="btn">Start Creating</Link>
          </div>
        </Reveal>
      </section>

      <footer>
        <div className="landfoot">
          <div>
            <b>SignalCraft AI</b>
            <p>Your personal AI content strategist.</p>
          </div>
          <div>
            <b>Product</b>
            <a href="#product">Features</a>
            <a href="#intelligence">Live demo</a>
            <a href="#agent">Agent</a>
          </div>
          <div>
            <b>Resources</b>
            <a href="https://github.com/Sanskar1724/signalcraft-ai" target="_blank" rel="noreferrer">Documentation</a>
            <a href="https://github.com/Sanskar1724/signalcraft-ai" target="_blank" rel="noreferrer">GitHub</a>
          </div>
          <div>
            <b>Creator</b>
            <p>Built by Sankiyy</p>
            <a href="https://github.com/Sanskar1724" target="_blank" rel="noreferrer" style={{ display: "inline-flex", gap: 6, alignItems: "center" }}>
              <GitHubIcon size={14} /> Sanskar1724
            </a>
          </div>
        </div>
        <div className="copy">© 2026 SignalCraft AI</div>
      </footer>
    </div>
  );
}
