from signalcraft import analytics
from signalcraft.content.generator import generate_content, list_content
from signalcraft.opportunities import build_opportunities
from signalcraft.profiles import seed_default_profile
from signalcraft.research import collect_and_store
from signalcraft.trends import detect_trends


def test_full_loop_offline(tmp_db):
    seed_default_profile()
    assert len(collect_and_store(limit=10, use_live=False)) >= 3
    trends = detect_trends()
    assert trends and trends[0]["score"] > 0
    # transparent formula spot-check (§10 configurable weights)
    t = trends[0]
    w = {"growth": 0.30, "freshness": 0.25, "relevance": 0.20,
         "source_momentum": 0.15, "novelty": 0.10}
    expect = 100 * (w["growth"] * t["growth"] + w["freshness"] * t["freshness"]
                    + w["relevance"] * t["relevance"]
                    + w["source_momentum"] * t["source_momentum"]
                    + w["novelty"] * t["novelty"])
    assert abs(expect - t["trend_score"]) < 0.15
    opps = build_opportunities()
    assert opps and {"topic", "why_now", "why_you", "score", "confidence"} <= set(opps[0])
    res = generate_content(opps[0]["id"], platform="LinkedIn")
    assert res["content"]["id"] > 0 and res["critique"]["overall"] >= 0
    assert len(list_content()) >= 1


def test_analytics_and_learning(tmp_db):
    seed_default_profile()
    collect_and_store(limit=10, use_live=False)
    opps = build_opportunities()
    res = generate_content(opps[0]["id"], platform="X")
    p = analytics.record_performance(res["content"]["id"], platform="X",
                                     impressions=1000, likes=50, comments=5, shares=2, saves=3)
    assert p["engagement_rate"] == 6.0
    s = analytics.summary()
    assert s["posts"] == 1 and s["best_topics"]
    from signalcraft.memory import get_memory_boost, learn_from_performance
    learn_from_performance()
    assert isinstance(get_memory_boost(1, opps[0]["topic"]), float)


def test_agent_uses_data(tmp_db):
    from signalcraft.agent import run
    seed_default_profile()
    collect_and_store(limit=10, use_live=False)
    build_opportunities()
    out = run("What should I post today?")
    assert "Observed fact" in out["answer"] and "trace" in out
    out2 = run("Analyze my last 10 posts.")
    assert out2["intent"] == "analyze"
