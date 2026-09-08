"""Pipeline integrity (§36-§37): HN junk, dedupe, personalization, agent
robustness, validation, versions. Uses crafted fixtures, never live calls.
"""
import json

from signalcraft import analytics
from signalcraft.content.generator import generate_content, validate
from signalcraft.content.sanitize import leak_found, scrub

HN_JUNK = (
    '<p>Article URL: <a href="https://example.com/ai-agents">https://example.com/ai-agents</a></p>'
    ' <p>Comments URL: <a href="https://news.ycombinator.com/item?id=1">https://news.ycombinator.com/item?id=1</a></p>'
    ' <p>Points: 128 | 45 comments</p>'
    " AI agents are changing data pipeline development with tool-calling models."
)

BANNED = ["https", "href", "url", "comments", "item", "points", "com"]


def _seed_research(conn, user_id, docs, base="https://example.com/x"):
    from signalcraft.db import new_uuid
    for i, (title, summary) in enumerate(docs):
        conn.execute(
            "INSERT INTO research_documents (uuid, user_id, source, source_url, title,"
            " summary, published_at) VALUES (?,?,?,?,?,?,?)",
            (new_uuid(), user_id, "rss", f"{base}/{user_id}/{i}", title, summary,
             "2026-09-06 10:00:00"),
        )
    conn.commit()


def test_hn_junk_never_becomes_trends(tmp_db):
    from signalcraft.db import get_conn
    from signalcraft.profiles import seed_default_profile
    from signalcraft.trends import detect_trends
    seed_default_profile()
    conn = get_conn()
    try:
        _seed_research(conn, 1, [
            ("AI agents reshape data pipelines", HN_JUNK),
            ("AI agents automate ETL work", HN_JUNK),
            ("LLM infrastructure costs fall", "LLM serving costs fall as inference improves."),
        ])
    finally:
        conn.close()
    trends = detect_trends()
    assert trends
    for t in trends:
        for bad in BANNED:
            assert bad not in t["topic"].split(), f"junk topic: {t['topic']}"
    assert any("agents" in t["topic"] for t in trends)


def test_duplicate_research_and_topics(tmp_db):
    from signalcraft.db import get_conn
    from signalcraft.profiles import seed_default_profile
    from signalcraft.research import collect_and_store
    from signalcraft.trends import detect_trends
    seed_default_profile()
    collect_and_store(limit=10, use_live=False)
    collect_and_store(limit=10, use_live=False)  # idempotent, no dup rows
    conn = get_conn()
    try:
        n = conn.execute("SELECT COUNT(*) AS n FROM research_documents").fetchone()["n"]
    finally:
        conn.close()
    assert n == 3
    topics = [t["topic"] for t in detect_trends()]
    assert len(topics) == len(set(topics))


def test_personalization_differs_per_creator(tmp_db):
    from signalcraft import auth
    from signalcraft.db import get_conn
    from signalcraft.profiles import update_profile
    from signalcraft.trends import detect_trends
    seed = auth.get_user(1)
    update_profile(1, niche="AI + Data Engineering", topics=["AI agents", "PySpark"])
    u2 = auth.create_user("Founder", "f@example.com", "password123")
    update_profile(u2["id"], niche="SaaS + Product Management",
                   topics=["Product strategy", "Startup growth"])
    conn = get_conn()
    try:
        _seed_research(conn, 1, [("AI agents reshape pipelines", "AI agents and PySpark ETL."),
                                 ("SaaS pricing strategy guide", "SaaS product strategy pricing.")])
        _seed_research(conn, u2["id"], [("AI agents reshape pipelines", "AI agents and PySpark ETL."),
                                        ("SaaS pricing strategy guide", "SaaS product strategy pricing.")])
    finally:
        conn.close()
    top1 = detect_trends(user_id=1)[0]["topic"]
    top2 = detect_trends(user_id=u2["id"])[0]["topic"]
    assert top1 != top2, f"same top topic for different creators: {top1}"
    assert seed["id"] == 1


def test_leak_scrub_and_gate(tmp_db):
    dirty = ("[Mock strategy abc] Goal here.\nThe user says write this.\n"
             "Creator niche: AI.\nReal sentence about agents.")
    assert leak_found(dirty)
    clean = scrub(dirty)
    assert not leak_found(clean) and "Real sentence" in clean
    assert scrub(scrub(clean)) == clean  # idempotent
    bad = validate("The user says we need to write. " + "Agents rock. " * 20)
    assert not bad["ok"] and any("leakage" in e for e in bad["errors"])
    assert not validate("x").get("ok")
    assert not validate("ok body. " * 30, platform="Nope")["ok"]
    assert not validate("short " * 3, platform="Blog")["ok"]


def test_agent_handles_corruption_and_emptiness(tmp_db, monkeypatch):
    from signalcraft import auth
    from signalcraft.agent import run
    from signalcraft.db import get_conn, new_uuid
    from signalcraft.profiles import seed_default_profile
    from signalcraft.research import collect_and_store
    seed_default_profile()
    collect_and_store(limit=5, use_live=False)
    from signalcraft.opportunities import build_opportunities
    build_opportunities()
    conn = get_conn()
    try:
        conn.execute(
            "INSERT INTO content_opportunities (uuid, user_id, topic, why_now, why_you,"
            " audience, angle, format, platform, score, confidence) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
            (new_uuid(), 1, "https href", "x", "y", "a", "angle", "f", "Blog", 1.0, 0.2))
        conn.commit()
    finally:
        conn.close()
    out = run("What should I post today?")
    assert "Observed fact" in out["answer"]
    for bad in BANNED:
        assert bad not in out["answer"].split()
    # brand-new user, zero data
    u2 = auth.create_user("New", "n@example.com", "password123")
    out2 = run("What should I post today?", user_id=u2["id"])
    assert "no opportunities" in out2["answer"].lower() or "Observed fact" in out2["answer"]
    # tool failure degrades gracefully, never 500s internally
    import signalcraft.agent as agent_mod
    monkeypatch.setattr(agent_mod, "list_opportunities",
                        lambda *a, **k: (_ for _ in ()).throw(RuntimeError("db down")))
    out3 = run("What should I post today?")
    assert "limitation" in out3["answer"].lower() or "Observed fact" in out3["answer"]

def test_analytics_missing_data(tmp_db):
    s = analytics.summary()
    assert s["posts"] == 0 and s["avg_engagement"] == 0.0
    assert analytics.insights() and "first piece" in analytics.insights()[0].lower()


def test_bad_topics_rejected(tmp_db):
    from signalcraft.db import get_conn
    from signalcraft.profiles import seed_default_profile
    from signalcraft.trends import detect_trends
    seed_default_profile()
    conn = get_conn()
    try:
        _seed_research(conn, 1, [
            ("Agents can use tools daily", "AI agents can use tools daily for ETL work."),
            ("Windows WSL setup notes", "Windows WSL setup notes for developers."),
            ("AI agents reshape data pipelines", "AI agents and PySpark ETL."),
        ])
    finally:
        conn.close()
    topics = [t["topic"] for t in detect_trends()]
    joined = " ".join(topics)
    for bad in ("agents can", "windows wsl"):
        assert bad not in joined, f"junk topic surfaced: {bad}"
    assert any("agents" in t for t in topics)


def test_angle_is_one_clean_sentence(tmp_db):
    from signalcraft.opportunities import build_opportunities, list_opportunities
    from signalcraft.profiles import seed_default_profile
    from signalcraft.research import collect_and_store
    seed_default_profile()
    collect_and_store(limit=5, use_live=False)
    build_opportunities()
    for o in list_opportunities():
        assert o["angle"] and len(o["angle"]) <= 200
        assert not leak_found(o["angle"]), o["angle"]
        assert "freshness" not in o["why_now"] and "growth" not in o["why_now"]
        assert o["evidence_titles"], "opportunity must carry evidence"


def test_regenerate_on_empty_then_fail(tmp_db):
    from signalcraft.content.generator import generate_content
    from signalcraft.llm import LLMGateway
    from signalcraft.llm.providers import BaseProvider, MockProvider
    from signalcraft.opportunities import build_opportunities
    from signalcraft.profiles import seed_default_profile
    from signalcraft.research import collect_and_store
    seed_default_profile()
    collect_and_store(limit=5, use_live=False)
    opps = build_opportunities()
    from signalcraft.llm.providers import LLMResult

    class Flaky(BaseProvider):
        name = "flaky"

        def __init__(self):
            self.calls = 0

        def generate(self, prompt, task="generation", max_tokens=800):
            self.calls += 1
            if self.calls == 1:
                return LLMResult("", "flaky", "f", 1, 10, 0)
            return MockProvider().generate(prompt, task, max_tokens)

    res = generate_content(opps[0]["id"], platform="LinkedIn",
                           gateway=LLMGateway(provider=Flaky()), persist=False)
    assert len(res["content"]["body"]) > 100

    class Empty(BaseProvider):
        name = "empty"

        def generate(self, prompt, task="generation", max_tokens=800):
            return LLMResult("   ", "empty", "e", 1, 10, 0)

    import pytest as _pt
    with _pt.raises(ValueError, match="no usable content"):
        generate_content(opps[0]["id"], platform="LinkedIn",
                         gateway=LLMGateway(provider=Empty()), persist=False)


def test_create_matrix_all_platforms(tmp_db):
    from signalcraft.content.generator import generate_content
    from signalcraft.opportunities import build_opportunities
    from signalcraft.profiles import seed_default_profile
    from signalcraft.research import collect_and_store
    seed_default_profile()
    collect_and_store(limit=5, use_live=False)
    opps = build_opportunities()
    for plat in ("LinkedIn", "X", "Blog", "Newsletter"):
        res = generate_content(opps[0]["id"], platform=plat, persist=False)
        body = res["content"]["body"]
        assert len(body) > 100, plat
        assert not leak_found(body), (plat, body[:200])
    x = generate_content(opps[0]["id"], platform="X", persist=False)["content"]["body"]
    li = generate_content(opps[0]["id"], platform="LinkedIn", persist=False)["content"]["body"]
    assert x != li, "platforms must not be mechanical copies"


def test_arjun_scenario_end_to_end(tmp_db):
    """§37: SaaS founder + HN research → clean loop, no artifacts anywhere."""
    from signalcraft import analytics
    from signalcraft.agent import run as agent_run
    from signalcraft.auth import create_user
    from signalcraft.content.generator import generate_content
    from signalcraft.db import get_conn
    from signalcraft.memory import learn_from_performance
    from signalcraft.opportunities import build_opportunities
    from signalcraft.profiles import update_profile
    from signalcraft.trends import detect_trends
    u = create_user("Arjun Mehta", "arjun@example.com", "password123")
    update_profile(u["id"], niche="SaaS + Startup + Product Management",
                   expertise="Product building", expertise_level="Advanced",
                   audience="Startup founders, product managers, SaaS builders",
                   goals=["Authority", "Audience Growth", "Leads"],
                   tone="Professional + Conversational + Opinionated",
                   topics=["AI-native SaaS", "Product strategy", "Startup growth"],
                   avoid_topics=["clickbait"], platforms=["LinkedIn", "X", "Blog"])
    conn = get_conn()
    try:
        _seed_research(conn, u["id"], [
            ("AI-native SaaS changes pricing models", HN_JUNK.replace("AI agents", "AI-native SaaS")),
            ("Product discovery with AI copilots", "AI copilots speed product discovery interviews."),
            ("LLM infrastructure costs fall", "LLM serving costs fall as inference improves."),
        ])
    finally:
        conn.close()
    trends = detect_trends(user_id=u["id"])
    assert trends
    blob = " ".join(t["topic"] for t in trends)
    for bad in BANNED:
        assert bad not in blob.split()
    opps = build_opportunities(user_id=u["id"])
    assert opps and opps[0]["score"] > 0
    res = generate_content(opps[0]["id"], platform="LinkedIn", user_id=u["id"])
    body = res["content"]["body"]
    assert not leak_found(body)
    assert "Mock" not in body and "brief" not in body.lower().split()
    saved_in_lib = res["content"]["id"] > 0
    assert saved_in_lib
    analytics.record_performance(res["content"]["id"], platform="LinkedIn",
                                 impressions=3000, likes=240, comments=30, shares=12)
    assert learn_from_performance(user_id=u["id"]) != []
    out = agent_run("What should I post today?", user_id=u["id"])
    assert "Observed fact" in out["answer"]
    for bad in BANNED:
        assert bad not in out["answer"].split()
