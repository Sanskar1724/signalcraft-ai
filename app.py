"""SignalCraft AI — personal AI content strategist. Streamlit dashboard (§17, §30)."""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from signalcraft import analytics, calendar, jobs  # noqa: E402
from signalcraft.agent import run as agent_run  # noqa: E402
from signalcraft.content.generator import generate_content, list_content  # noqa: E402
from signalcraft.db import init_db  # noqa: E402
from signalcraft.memory import learn_from_performance, recall, remember_feedback  # noqa: E402
from signalcraft.opportunities import build_opportunities, list_opportunities  # noqa: E402
from signalcraft.profiles import get_profile, seed_default_profile, update_profile  # noqa: E402
from signalcraft.research import collect_and_store, list_recent  # noqa: E402
from signalcraft.trends import detect_trends  # noqa: E402

st.set_page_config(page_title="SignalCraft AI", page_icon="◉", layout="wide")
init_db()

NAV = ["Overview", "Trending For You", "Content Opportunities", "Create",
       "Content Library", "Analytics", "Calendar", "AI Insights", "Agent",
       "Settings"]


@st.cache_data(ttl=900, show_spinner=False)
def _cached_opps(limit: int = 20):
    return list_opportunities(limit=limit)


@st.cache_data(ttl=900, show_spinner=False)
def _cached_summary():
    return analytics.summary()


def _bust_cache():
    st.cache_data.clear()

with st.sidebar:
    st.title("◉ SignalCraft AI")
    st.caption("Your personal AI content strategist.")
    page = st.radio("Navigate", NAV)
    st.divider()
    if st.button("Seed demo profile"):
        seed_default_profile()
        st.success("Demo profile loaded.")
    if st.button("Refresh research + trends"):
        with st.spinner("Collecting research…"):
            jobs.run_refresh(limit=20, use_live=True)
            _bust_cache()
        st.success("Research, trends and opportunities updated.")

profile = get_profile()

# ---------- Overview ----------
if page == "Overview":
    st.header("What should you talk about right now?")
    opps = _cached_opps(3)
    recent = list_recent(limit=5)
    s = _cached_summary()
    c1, c2, c3 = st.columns(3)
    c1.metric("Opportunities", len(list_opportunities(limit=50)))
    c2.metric("Posts tracked", s["posts"])
    c3.metric("Avg engagement %", s["avg_engagement"])
    st.subheader("Top recommendations")
    if not opps:
        st.info("No opportunities yet. Click 'Refresh research + trends' in the sidebar.")
    for o in opps:
        with st.container(border=True):
            st.markdown(f"**{o['topic']}** — {o['score']}/100 · conf {o['confidence']}")
            st.caption(f"Why now: {o['why_now'][:220]}")
            st.caption(f"Why you: {o['why_you'][:220]}")
    st.subheader("Fresh research")
    if not recent:
        st.info("No research yet.")
    for r in recent:
        st.markdown(f"- {r['title']} `[{r['source']}]`")
        if r["source_url"] and not r["source_url"].startswith("sample://"):
            st.caption(r["source_url"])

# ---------- Trending ----------
elif page == "Trending For You":
    st.header("Trending — filtered for you")
    st.caption("Score = 100 × (0.20 freshness + 0.15 growth + 0.20 relevance + "
               "0.15 audience fit + 0.10 novelty + 0.05 (1 − competition) + 0.15 creator fit).")
    trends = detect_trends()
    if not trends:
        st.info("No trends. Refresh research first.")
    else:
        df = pd.DataFrame(trends)
        st.bar_chart(df.set_index("topic")["score"])
        for t in trends:
            with st.expander(f"{t['topic']} — {t['score']}"):
                st.write(f"Freshness {t['freshness']} · Growth {t['growth']} · "
                         f"Relevance {t['relevance']} · Audience fit {t.get('audience_fit')} · "
                         f"Novelty {t['novelty']} · Competition {t.get('competition')} · "
                         f"Creator fit {t.get('creator_fit')}")
                st.write("Evidence:")
                for e in t["evidence_titles"][:3]:
                    st.markdown(f"- {e}")

# ---------- Opportunities ----------
elif page == "Content Opportunities":
    st.header("Personalized opportunities")
    opps = _cached_opps(20)
    if not opps:
        st.info("No opportunities. Refresh research first.")
    for o in opps:
        with st.container(border=True):
            st.markdown(f"### {o['topic']} — {o['score']}/100")
            st.markdown("**Observed fact**")
            st.write(o["why_now"])
            st.markdown("**AI interpretation**")
            st.write(o["why_you"])
            st.markdown("**AI recommendation**")
            st.write(f"Angle: {o['angle']}")
            st.caption(f"Audience: {o['audience']} · Platform: {o['platform']} · "
                       f"Confidence: {o['confidence']} · Format: {o['format']}")

# ---------- Create ----------
elif page == "Create":
    st.header("Create platform-ready content")
    opps = list_opportunities(limit=20)
    if not opps:
        st.info("Generate opportunities first.")
    else:
        labels = {f"{o['topic']} ({o['score']})": o["id"] for o in opps}
        choice = st.selectbox("Opportunity", list(labels))
        plat = st.selectbox("Platform", ["LinkedIn", "X", "Blog"])
        if st.button("Generate", type="primary"):
            with st.spinner("Strategy → draft → critique → validate…"):
                try:
                    res = generate_content(labels[choice], platform=plat)
                    st.session_state["last_content"] = res["content"]
                    st.session_state["last_critique"] = res["critique"]
                    _bust_cache()
                except Exception as e:
                    st.error(f"Generation failed: {e}")
        if "last_content" in st.session_state:
            c = st.session_state["last_content"]
            q = st.session_state["last_critique"]
            st.success(f"Quality {q['overall']}/10 — {q['suggestion']}")
            st.text_area("Draft", c["body"], height=320)
            with st.expander("Critique detail"):
                st.json(q["scores"])

# ---------- Library ----------
elif page == "Content Library":
    st.header("Content library")
    items = list_content()
    if not items:
        st.info("Nothing here yet. Create your first draft.")
    for c in items:
        with st.expander(f"[{c['platform']}] {c['title'][:70]} — Q{c['quality_score']}"):
            st.write(c["body"])
            st.caption(f"Topic: {c.get('opportunity_topic') or '—'} · {c['created_at']}")
            fb_col1, fb_col2 = st.columns(2)
            if fb_col1.button("👍 Useful", key=f"up{c['id']}"):
                remember_feedback(1, c.get("opportunity_topic") or c["title"], True)
                st.success("Noted — future recommendations will adapt.")
            if fb_col2.button("👎 Not for me", key=f"dn{c['id']}"):
                remember_feedback(1, c.get("opportunity_topic") or c["title"], False)
                st.success("Noted.")

# ---------- Analytics ----------
elif page == "Analytics":
    st.header("Performance")
    s = _cached_summary()
    if s["posts"] == 0:
        st.info("Log performance for a post to unlock analytics.")
    else:
        st.metric("Avg engagement %", s["avg_engagement"])
        df = pd.DataFrame(s["rows"])
        if not df.empty:
            st.bar_chart(df.set_index("id")["engagement_rate"])
            cols = [c for c in ["id", "platform", "topic", "impressions", "likes",
                                "comments", "shares", "reach", "engagement_rate"] if c in df.columns]
            st.dataframe(df[cols])
        if s.get("best_formats"):
            st.subheader("Best formats")
            for f_ in s["best_formats"][:3]:
                st.markdown(f"- {f_.get('platform')}: {f_['avg_engagement']}%")
    st.subheader("Log performance (manual entry, §15)")
    items = list_content(limit=50)
    if items:
        cmap = {f"#{c['id']} [{c['platform']}] {c['title'][:50]}": c["id"] for c in items}
        sel = st.selectbox("Post", list(cmap))
        with st.form("perf"):
            a = st.number_input("Impressions", 0, step=100)
            b = st.number_input("Likes", 0)
            cc = st.number_input("Comments", 0)
            d = st.number_input("Shares", 0)
            e = st.number_input("Clicks", 0)
            f = st.number_input("Saves", 0)
            g = st.number_input("Reach", 0, step=100)
            if st.form_submit_button("Save"):
                try:
                    analytics.record_performance(cmap[sel], impressions=int(a), likes=int(b),
                                                 comments=int(cc), shares=int(d),
                                                 clicks=int(e), saves=int(f), reach=int(g))
                    _bust_cache()
                    st.success("Saved.")
                except Exception as ex:
                    st.error(str(ex))

# ---------- Calendar ----------
elif page == "Calendar":
    st.header("Content calendar")
    with st.form("sched"):
        plat = st.selectbox("Platform", ["LinkedIn", "X", "Blog"])
        when = st.text_input("Scheduled for (YYYY-MM-DD HH:MM)", "2026-09-10 10:00")
        notes = st.text_input("Notes", "")
        if st.form_submit_button("Schedule"):
            calendar.schedule(1, plat, when, notes=notes)
            st.success("Scheduled.")
    for en in calendar.upcoming():
        st.markdown(f"- **{en['scheduled_for']}** [{en['platform']}] {en.get('title') or en['notes']} `{en['status']}`")

# ---------- Insights ----------
elif page == "AI Insights":
    st.header("What should you change?")
    for line in analytics.insights():
        st.markdown(f"- {line}")
    if st.button("Learn from performance → memory"):
        notes = learn_from_performance()
        st.success("; ".join(notes) if notes else "Nothing new.")
    st.subheader("Creator memory")
    mems = recall(limit=30)
    if not mems:
        st.info("Memory is empty. It fills as you log performance.")
    for m in mems:
        st.markdown(f"- `{m['kind']}` **{m['key']}** — {m['value']} (hits {m['hits']})")

# ---------- Agent ----------
elif page == "Agent":
    st.header("Ask your content agent")
    st.caption("Try: What should I post today? · Why is this topic relevant to me? · "
               "Analyze my last 10 posts · Turn this into a LinkedIn post.")
    q = st.text_input("Question")
    if st.button("Ask", type="primary") and q:
        with st.spinner("Consulting your data…"):
            try:
                res = agent_run(q)
            except Exception as e:
                st.error(f"Agent failed: {e}")
                res = None
        if res:
            st.write(res["answer"])
            with st.expander("Execution trace (observability)"):
                st.json(res["trace"])

# ---------- Settings ----------
elif page == "Settings":
    st.header("Creator profile (§7)")
    st.caption("Everything — research, trends, generation — adapts to this.")
    with st.form("profile"):
        niche = st.text_input("Niche", profile.niche)
        expertise = st.text_input("Expertise", profile.expertise)
        audience = st.text_input("Audience", profile.audience)
        goals = st.text_input("Goals", profile.goals)
        tone = st.text_input("Tone", profile.tone)
        topics = st.text_input("Preferred topics (comma separated)", ", ".join(profile.topics))
        avoid = st.text_input("Topics to avoid", ", ".join(profile.avoid_topics))
        style = st.text_area("Style notes", profile.style_notes)
        content_prefs = st.text_area("Content preferences", profile.content_preferences)
        posting_prefs = st.text_input("Posting preferences", profile.posting_preferences)
        if st.form_submit_button("Save profile"):
            update_profile(1, niche=niche, expertise=expertise, audience=audience,
                           goals=goals, tone=tone,
                           topics=[t.strip() for t in topics.split(",") if t.strip()],
                           avoid_topics=[t.strip() for t in avoid.split(",") if t.strip()],
                           style_notes=style, content_preferences=content_prefs,
                           posting_preferences=posting_prefs)
            _bust_cache()
            st.success("Profile saved. Future recommendations will adapt.")
