import Link from "next/link";
import Logo from "../components/Logo";

function Section({ id, kicker, title, children }: { id: string; kicker: string; title: string; children: React.ReactNode }) {
  return (
    <section id={id} className="landsec">
      <p className="kicker">{kicker}</p>
      <h2 className="landh">{title}</h2>
      {children}
    </section>
  );
}

export default function Landing() {
  return (
    <div className="land">
      <header className="landnav">
        <Link href="/" className="landbrand"><Logo size={30} /><b>Signal<span>Craft</span></b></Link>
        <nav>
          <a href="#product">Product</a>
          <a href="#how">How it works</a>
          <a href="#intelligence">Intelligence</a>
          <a href="#analytics">Analytics</a>
          <a href="https://github.com/Sanskar1724/signalcraft-ai">GitHub</a>
        </nav>
        <div>
          <Link href="/login" className="btn ghost small">Sign In</Link>{" "}
          <Link href="/signup" className="btn small">Get Started</Link>
        </div>
      </header>

      <section className="hero">
        <p className="kicker">Personal AI content strategist</p>
        <h1>Stop guessing.<br />Start publishing what <em>matters</em>.</h1>
        <p className="lede">
          SignalCraft learns who you are, researches your niche every day, and tells you
          exactly what to post — then helps you write it, measures it, and gets smarter.
        </p>
        <div className="row">
          <Link href="/signup" className="btn">Get Started — it&apos;s free to try</Link>
          <Link href="#how" className="btn ghost">See how it works</Link>
        </div>
        <div className="signalstrip">
          <span className="pill li">AI Agents · trend 82</span>
          <span className="pill x">LLM pipelines · opportunity 91</span>
          <span className="pill blog">PySpark + AI · rising</span>
        </div>
      </section>

      <Section id="product" kicker="The problem" title="Generic AI writers don't know you.">
        <p className="lede">
          Prompt-to-paragraph tools treat a data engineer and a lifestyle influencer identically.
          SignalCraft starts from your profile — niche, audience, goals, style, history — and only
          then looks at the world.
        </p>
      </Section>

      <Section id="how" kicker="How it works" title="You → intelligence → content → learning.">
        <div className="grid3">
          <div className="card"><h3>1 · Tell it who you are</h3><p className="muted">A 7-step onboarding captures niche, audience, goals, style and platforms.</p></div>
          <div className="card"><h3>2 · Get your briefing</h3><p className="muted">Fresh research becomes trends scored for YOU, with reasons attached.</p></div>
          <div className="card"><h3>3 · Publish &amp; improve</h3><p className="muted">Platform-native drafts, critique loops, analytics that teach the system.</p></div>
        </div>
      </Section>

      <Section id="intelligence" kicker="Trend intelligence" title="Not what's trending. What's trending for you.">
        <div className="card glow">
          <h3>AI Agents + Data Engineering — opportunity 93/100</h3>
          <p><b>Observed fact.</b> 5 fresh sources, growth 0.8, momentum across RSS and community.</p>
          <p><b>Interpretation.</b> Matches your niche (relevance 0.9) and your developer audience.</p>
          <p><b>Recommendation.</b> “How AI agents are changing data pipeline development.” Best for LinkedIn + X.</p>
        </div>
      </Section>

      <Section id="product-gen" kicker="Content generation" title="One opportunity, three native voices.">
        <p className="lede">LinkedIn storytelling, X threads, long-form Blog — each rendered from platform rules and a validated brief, never truncated copies.</p>
      </Section>

      <Section id="brain" kicker="Personal content brain" title="It remembers what works for you.">
        <p className="lede">Winning topics, weak hooks, best formats, your feedback — stored as structured memory that re-ranks every future recommendation.</p>
      </Section>

      <Section id="analytics" kicker="Performance learning" title="Every post makes the next one smarter.">
        <p className="lede">Log impressions, likes, comments once. Analytics, insights and memory update automatically — the loop never breaks.</p>
      </Section>

      <Section id="agent" kicker="Content agent" title="Ask it anything about your strategy.">
        <div className="card">
          <p><b>You:</b> What should I post today?</p>
          <p className="muted"><b>SignalCraft:</b> Your top opportunity is “LLM pipelines” (91/100) — your last 3 technical posts averaged 9.4% engagement…</p>
        </div>
      </Section>

      <Section id="preview" kicker="Dashboard preview" title="Your morning briefing, in one screen.">
        <div className="grid3">
          <div className="metric hot"><b>8</b><span>opportunities ranked</span></div>
          <div className="metric"><b>21</b><span>drafts generated</span></div>
          <div className="metric"><b>9.4%</b><span>avg engagement</span></div>
        </div>
      </Section>

      <section className="landsec center">
        <h2 className="landh">Tell SignalCraft who you are.<br />It handles the rest.</h2>
        <p><Link href="/signup" className="btn">Build my content intelligence</Link></p>
      </section>

      <footer className="landfoot">
        <span>SignalCraft AI — personal AI content strategist.</span>
        <span><a href="https://github.com/Sanskar1724/signalcraft-ai">GitHub</a> · <Link href="/login">Sign In</Link></span>
      </footer>
    </div>
  );
}
