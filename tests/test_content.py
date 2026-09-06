from signalcraft.content.critic import critique


def test_critique_scores_range():
    body = ("AI agents in data pipelines: what changed.\n\n"
            "Teams use tool-calling agents to scaffold ETL with review gates. "
            "Example: backfill validation. Try one small task this week?")
    r = critique(body, platform="LinkedIn", topic="AI agents data")
    assert 0 <= r["overall"] <= 10
    assert set(r["scores"]) >= {"relevance", "hook", "cta", "evidence"}


def test_critique_catches_hype_and_short():
    r = critique("Hi.", platform="Blog", topic="agents")
    assert r["overall"] < 7.5
    assert r["issues"]


def test_x_thread_format_preferred():
    from signalcraft.content.platforms import format_x
    hook, body, _ = format_x("agents", "sharp angle", "core " * 100, "sharp")
    assert "1/" in body
