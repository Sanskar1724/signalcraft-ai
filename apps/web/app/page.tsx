"use client";

import Link from "next/link";
import React, { useState } from "react";
import Logo from "../components/Logo";
import { GitHubIcon } from "../components/Navbar";
import Navbar from "../components/Navbar";
import SignalField from "../components/SignalField";
import { Reveal } from "../components/fx";

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

const PLAT_EXAMPLES: Record<string, string> = {
  LinkedIn:
    "AI agents in data pipelines: what changed.\n\nTeams now scaffold ETL with tool-calling agents — with human review gates.\n\nTakeaway: automate the boilerplate, keep the judgment.\n\nWhat is working for you?",
  X: "1/ AI agents in data pipelines in one line: automate the boring parts, review the rest.\n\n2/ Context: tool-calling agents now scaffold ETL reliably.\n\n3/ Takeaway: try it on one backfill this week.",
  Blog: "# AI Agents in Data Pipelines: a practical guide\n\n> Angle: automate the boilerplate, keep the judgment.\n\n## Why now\nTool-calling agents crossed from demos to daily ETL work…",
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

        <div className="heroviz">
          <div className="floatcard">
            <p className="lbl">SignalCraft · Good morning, Sankiyy</p>
            <p className="lbl" style={{ marginTop: 10 }}>Trending for you</p>
            <h3>AI Agents + Data Engineering</h3>
            <div className="score"><span>Trend</span><b>94</b></div>
            <div className="score"><span>Audience Fit</span><b>97</b></div>
            <div className="score"><span>Freshness</span><b>96</b></div>
            <div className="score"><span>Opportunity</span><b style={{ color: "var(--accent)" }}>93</b></div>
            <p className="muted">“How AI agents are changing data pipeline development.”</p>
            <Link href="/signup" className="btn small">Generate Content</Link>
          </div>
        </div>

        <div className="signalstrip">
          <span className="pill li">Real-time Intelligence</span>
          <span className="pill x">Personal Strategy</span>
          <span className="pill blog">Multi-platform Creation</span>
          <span className="pill good">Performance Learning</span>
        </div>
      </section>

      <Section id="product" kicker="The problem" title="Most AI writing tools start with a blank box.">
        <div className="grid2">
          <div className="card">
            <p className="lbl">Generic path</p>
            <p className="muted">Prompt → Generic AI output → Generic content → No strategy → No learning</p>
          </div>
          <div className="card glow">
            <p className="lbl">SignalCraft path</p>
            <p>You + Your audience + Current trends + Your performance = <b>Personalized content intelligence</b></p>
          </div>
        </div>
      </Section>

      <Section id="how" kicker="How it works" title="A product story in five steps.">
        {[
          ["01", "Understand You", "Niche, audience, goals, style, history — captured once, used everywhere."],
          ["02", "Understand What Is Happening", "Fresh research from RSS, search and community sources, deduplicated."],
          ["03", "Find Your Opportunity", "Trends scored for you specifically, each with its reason."],
          ["04", "Create What Matters", "Brief-led drafts per platform, critiqued and revised."],
          ["05", "Learn What Works", "Performance becomes memory that re-ranks everything next."],
        ].map(([n, t, d]) => (
          <div className="howstep" key={n}>
            <span className="num">{n}</span>
            <div><h3>{t}</h3><p className="muted">{d}</p></div>
          </div>
        ))}
      </Section>

      <Section id="intelligence" kicker="Trend intelligence" title="Don't chase trends. Find your opportunity.">
        <div className="card glow">
          <p className="lbl">Trending for you</p>
          <h3>AI Agents + Data Engineering</h3>
          <div className="dims">
            <span>Trend Score <b>94</b></span><span>Audience Fit <b>97</b></span>
            <span>Freshness <b>96</b></span><span>Competition <b>Medium</b></span>
          </div>
          <p><b>Opportunity Score — 93.</b> Strong alignment with your niche and current audience interest.</p>
          <p className="muted">Recommended angle: “How AI agents are changing data pipeline development.”</p>
          <Link href="/signup" className="btn small">Create Content</Link>
        </div>
      </Section>

      <Section id="generation" kicker="Content generation" title="One idea, three native voices.">
        <PlatformTabs />
      </Section>

      <Section id="brain" kicker="Personal content brain" title="SignalCraft learns what works for you.">
        <div className="card">
          <p className="lbl">Your content brain</p>
          {[["Writing Style", "Technical + Simple"], ["Best Topic", "AI Agents"], ["Best Format", "Project Story"],
            ["Best Platform", "LinkedIn"], ["Audience", "Developers"], ["Strong Pattern", "Technical storytelling"]].map(([k, v]) => (
            <div className="braintile" key={k}><span className="muted">{k}</span><b>{v}</b></div>
          ))}
        </div>
      </Section>

      <Section id="analytics" kicker="Performance learning" title="Content → performance → insight → memory.">
        <div className="card">
          {[["AI Agents", 96], ["Data Engineering", 72], ["Generic AI News", 24]].map(([t, w]) => (
            <div key={t as string}>
              <p style={{ margin: "8px 0 2px", fontSize: 13 }}>{t}</p>
              <div className="bar"><i style={{ width: `${w}%` }} /></div>
            </div>
          ))}
          <p style={{ marginTop: 14 }}><b>AI insight.</b> <span className="muted">Technical AI content is outperforming generic AI news for your audience. Create more technical story-driven content.</span></p>
        </div>
      </Section>

      <Section id="agent" kicker="AI agent" title="Just ask your content agent.">
        <div className="agentmock">
          <div className="q"><b>You:</b> What should I post today?</div>
          <div className="a">I found three opportunities aligned with your audience. The strongest is AI agents in data engineering.</div>
          <div className="q"><b>You:</b> Make it technical.</div>
          <div className="a">Here&apos;s a technical LinkedIn angle…</div>
          <div className="q"><b>You:</b> Turn it into an X thread.</div>
          <div className="a">Done.</div>
        </div>
      </Section>

      <Section id="preview" kicker="Dashboard preview" title="Your morning briefing, in one screen.">
        <div className="browser">
          <div className="browserbar"><i /><i /><i /></div>
          <div className="browserbody">
            <p className="lbl">Overview · Good morning, Sankiyy</p>
            <div className="grid3">
              <div className="metric"><b>+24%</b><span>engagement</span></div>
              <div className="metric"><b>12</b><span>opportunities</span></div>
              <div className="metric"><b>18</b><span>posts this month</span></div>
            </div>
            <p style={{ marginTop: 12 }}><b>Trending for you:</b> <span className="muted">AI Agents · AI + Data Pipelines · LLM Infrastructure</span></p>
            <p><b>AI insight:</b> <span className="muted">Your technical AI posts are performing above your average.</span></p>
          </div>
        </div>
      </Section>

      <section className="landsec center">
        <Reveal>
          <h2 className="landh">Stop guessing what to post.</h2>
          <p className="lede">Let SignalCraft research, strategize, create, and learn with you.</p>
          <div className="row" style={{ justifyContent: "center" }}>
            <Link href="/signup" className="btn">Start Creating</Link>
            <a href="https://github.com/Sanskar1724/signalcraft-ai" target="_blank" rel="noreferrer" className="btn ghost">Explore GitHub</a>
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
            <a href="#intelligence">Intelligence</a>
            <a href="#analytics">Analytics</a>
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
