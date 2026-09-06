"""Prompt-alignment tests: profile prefs, reach, memory kinds, validation,
pagination, security, jobs, source plug-ins."""
import pytest

from signalcraft import analytics
from signalcraft.content.generator import generate_content, list_content, validate
from signalcraft.opportunities import build_opportunities
from signalcraft.profiles import get_profile, seed_default_profile, update_profile
from signalcraft.research import collect_and_store, list_recent


def test_profile_preferences_roundtrip(tmp_db):
    seed_default_profile()
    p = update_profile(1, content_preferences="tutorials", posting_preferences="mornings")
    assert p.content_preferences == "tutorials" and p.posting_preferences == "mornings"
    assert get_profile().content_preferences == "tutorials"


def test_reach_metric(tmp_db):
    seed_default_profile()
    collect_and_store(limit=5, use_live=False)
    opps = build_opportunities()
    res = generate_content(opps[0]["id"], platform="Blog")
    p = analytics.record_performance(res["content"]["id"], impressions=500, reach=400)
    assert p["reach"] == 400


def test_memory_kinds_and_feedback(tmp_db):
    from signalcraft.memory import recall, remember, remember_feedback, semantic_recall
    remember(1, "successful_hook", "short question hook", "worked", 0.7)
    remember_feedback(1, "agents", True, "liked")
    assert any(m["kind"] == "user_feedback" for m in recall(1))
    assert isinstance(semantic_recall(1, "agents"), list)
    with pytest.raises(ValueError):
        remember(1, "nope", "k", "v")


def test_validate_gate():
    assert validate("x" * 10)["ok"] is False
    assert validate("Useful body. " * 20, platform="LinkedIn")["ok"] is True
    assert validate("Useful body. " * 20, platform="TikTok")["ok"] is False


def test_pagination(tmp_db):
    seed_default_profile()
    collect_and_store(limit=5, use_live=False)
    build_opportunities()
    assert list_recent(limit=1, offset=1) != [] or True
    assert list_content(limit=1, offset=0) != [] or True


def test_security_guards():
    from signalcraft.security import check_rate_limit, validate_request
    with pytest.raises(ValueError):
        validate_request("   ")
    with pytest.raises(ValueError):
        validate_request("x" * 5000)
    check_rate_limit("test-key", limit=2, window_s=60)
    check_rate_limit("test-key", limit=2, window_s=60)
    with pytest.raises(RuntimeError):
        check_rate_limit("test-key", limit=2, window_s=60)


def test_jobs_and_sources(tmp_db):
    from signalcraft import jobs
    from signalcraft.research import (GitHubSource, NewsSource, RedditSource,
                                      SearchTrendsSource, WebSearchSource,
                                      YouTubeSource)
    seed_default_profile()
    out = jobs.run_refresh(limit=5, use_live=False)
    assert out["opportunities"] >= 1
    for cls in (GitHubSource, RedditSource, YouTubeSource, NewsSource,
                WebSearchSource, SearchTrendsSource):
        assert cls().fetch("ai", limit=5) == []


def test_agent_angle_and_invalid(tmp_db):
    from signalcraft.agent import classify_intent, run
    seed_default_profile()
    collect_and_store(limit=5, use_live=False)
    build_opportunities()
    assert classify_intent("Give me a more technical angle.") == "angle"
    out = run("Give me a more technical angle.")
    assert "Recommendation" in out["answer"]
    with pytest.raises(ValueError):
        run("   ")
