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


def test_grounding_toggle(tmp_db):
    from signalcraft.content.generator import generate_content
    from signalcraft.opportunities import build_opportunities
    from signalcraft.profiles import seed_default_profile
    from signalcraft.research import collect_and_store
    seed_default_profile()
    collect_and_store(limit=5, use_live=False)
    opps = build_opportunities()
    full = generate_content(opps[0]["id"], platform="LinkedIn", grounded=True)
    assert full["brief"].supporting_evidence, "grounded brief must carry evidence"
    bare = generate_content(opps[0]["id"], platform="LinkedIn", grounded=False,
                            persist=False)
    assert bare["brief"].supporting_evidence == []


def test_style_reference_uses_real_top_post(tmp_db):
    from signalcraft import analytics
    from signalcraft.content.generator import _style_reference, generate_content
    from signalcraft.opportunities import build_opportunities
    from signalcraft.profiles import seed_default_profile
    from signalcraft.research import collect_and_store
    seed_default_profile()
    collect_and_store(limit=5, use_live=False)
    opps = build_opportunities()
    assert _style_reference(1, "LinkedIn") == ""
    res = generate_content(opps[0]["id"], platform="LinkedIn")
    analytics.record_performance(res["content"]["id"], platform="LinkedIn",
                                 impressions=2000, likes=200)
    ref = _style_reference(1, "LinkedIn")
    assert ref and "10.0%" in ref
    res2 = generate_content(opps[0]["id"], platform="LinkedIn", style_match=True,
                            persist=False)
    assert res2["brief"].style_reference != ""
    res3 = generate_content(opps[0]["id"], platform="LinkedIn", style_match=False,
                            persist=False)
    assert res3["brief"].style_reference == ""


def test_no_json_keys_or_labels_in_outputs(tmp_db):
    from signalcraft.content.generator import brief_to_prose, build_brief, generate_content
    from signalcraft.content.sanitize import leak_found
    from signalcraft.llm.prompts import render
    from signalcraft.opportunities import build_opportunities
    from signalcraft.profiles import get_profile, seed_default_profile
    from signalcraft.research import collect_and_store
    seed_default_profile()
    collect_and_store(limit=5, use_live=False)
    opps = build_opportunities()
    profile = get_profile()
    brief = build_brief(profile, opps[0], ["fact one", "fact two"], {}, "voice ref")
    prose = brief_to_prose(brief, profile)
    for token in ("supporting_evidence", "style_reference", "target_audience", "core_message"):
        assert token not in prose
        assert token not in render("linkedin_generation", brief_prose=prose, tone="x")
    assert profile.niche.split("+")[0].strip().lower() in prose.lower()
    for plat in ("LinkedIn", "X", "Blog", "Newsletter"):
        body = generate_content(opps[0]["id"], platform=plat, persist=False)["content"]["body"]
        assert "Angle:" not in body and "Context:" not in body
        assert not leak_found(body)


def test_critic_technical_value_and_provider(tmp_db):
    from signalcraft.content.critic import critique
    from signalcraft.content.generator import generate_content
    from signalcraft.opportunities import build_opportunities
    from signalcraft.profiles import seed_default_profile
    from signalcraft.research import collect_and_store
    seed_default_profile()
    collect_and_store(limit=5, use_live=False)
    opps = build_opportunities()
    res = generate_content(opps[0]["id"], platform="Blog", persist=False)
    assert "technical_value" in res["critique"]["scores"]
    assert res["provider"] == "mock"
    thin = critique("Too short.", platform="Blog")
    assert thin["overall"] <= 3.0
