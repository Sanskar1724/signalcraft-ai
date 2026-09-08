"""API tests (§26): profile, research, trends, opportunities, generation, analytics, agent, auth."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))


@pytest.fixture()
def client(tmp_path, monkeypatch):
    from signalcraft import config, db
    monkeypatch.setattr(config.settings, "db_path", tmp_path / "api.db")
    monkeypatch.setattr(config.settings, "api_key", "")
    monkeypatch.setattr(config.settings, "openrouter_api_key", "")
    monkeypatch.setattr(config.settings, "openai_api_key", "")
    monkeypatch.setattr(config.settings, "google_client_id", "")
    monkeypatch.setattr(config.settings, "google_client_secret", "")
    db.init_db(tmp_path / "api.db")
    from apps.api.app.main import app
    from fastapi.testclient import TestClient
    with TestClient(app) as c:
        yield c


def test_health(client):
    r = client.get("/api/health")
    assert r.status_code == 200 and r.json()["ok"] is True
    assert r.headers.get("X-Request-ID")


def test_cors_preflight(client):
    from signalcraft import config
    origin = [o.strip() for o in config.settings.cors_origins.split(",") if o.strip()][0]
    r = client.options(
        "/api/trends",
        headers={"Origin": origin, "Access-Control-Request-Method": "GET"},
    )
    assert r.status_code == 200
    assert r.headers.get("access-control-allow-origin") == origin


def test_profile_roundtrip(client):
    assert client.get("/api/profile").status_code == 200
    r = client.put("/api/profile", json={"niche": "AI + Data", "tone": "crisp"})
    assert r.status_code == 200 and r.json()["niche"] == "AI + Data"


def test_full_flow(client):
    assert client.post("/api/research", json={"limit": 5, "use_live": False}).status_code == 200
    trends = client.get("/api/trends").json()
    assert trends and trends[0]["trend_score"] > 0
    opps = client.get("/api/opportunities", params={"refresh": True}).json()
    assert opps and opps[0]["score"] > 0
    gen = client.post("/api/content/generate",
                      json={"opportunity_id": opps[0]["id"], "platform": "LinkedIn"}).json()
    assert gen["persisted"] is False and gen["content"]["id"] is None
    assert gen["brief"]["topic"] == opps[0]["topic"]
    assert "Mock" not in gen["content"]["body"] and "brief" not in gen["content"]["body"].lower()
    saved = client.post("/api/content/save", json={
        "opportunity_id": opps[0]["id"], "platform": "LinkedIn",
        "title": gen["content"]["title"], "body": gen["content"]["body"],
        "hook": gen["content"]["hook"], "brief": gen["brief"]}).json()
    cid = saved["content"]["id"]
    assert saved["content"]["id"] > 0
    # saving the same body twice is rejected
    assert client.post("/api/content/save", json={
        "platform": "LinkedIn", "title": "x", "body": gen["content"]["body"]}).status_code == 400
    # leaked internals are rejected at save
    assert client.post("/api/content/save", json={
        "platform": "LinkedIn", "title": "x",
        "body": "The user says we need to write about " + "agents. " * 20}).status_code == 400
    crit = client.post("/api/content/critique",
                       json={"body": gen["content"]["body"], "platform": "LinkedIn"}).json()
    assert crit["overall"] >= 0
    imp = client.post("/api/content/improve-preview",
                      json={"body": gen["content"]["body"], "platform": "LinkedIn"}).json()
    assert imp["body"] and imp["critique"]["overall"] >= 0
    rev = client.post("/api/content/revise", json={"content_id": cid}).json()
    assert rev["version"] == 2
    items = client.get("/api/content").json()
    assert len(items) >= 1
    detail = client.get(f"/api/content/{cid}").json()
    assert len(detail["versions"]) == 2 and detail["brief"]
    assert detail["versions"][0]["body"] != detail["versions"][1]["body"]
    perf = client.post(f"/api/content/{cid}/performance",
                       json={"impressions": 1000, "likes": 60}).json()
    assert perf["engagement_rate"] == 6.0
    assert client.get("/api/analytics").json()["posts"] >= 1
    assert client.get("/api/insights").json()["insights"]
    chat = client.post("/api/agent/chat", json={"message": "What should I post today?"}).json()
    assert "Observed fact" in chat["answer"] and chat["request_id"]
    assert chat["trace"]["steps"]
    assert "user says" not in chat["answer"].lower()
    assert chat["actions"] and chat["actions"][0]["href"].startswith("/app/")
    assert client.post("/api/agent/learn").json()["learned"]
    assert client.get("/api/debug/llm").json()["usage"]
    assert client.put(f"/api/opportunities/{opps[0]['id']}/dismiss").json()["ok"] is True
    remaining = client.get("/api/opportunities").json()
    assert all(o["id"] != opps[0]["id"] for o in remaining)


def test_validation_and_404_envelope(client):
    r = client.post("/api/content/critique", json={"body": "", "platform": "LinkedIn"})
    assert r.status_code == 422
    r = client.get("/api/content/9999")
    assert r.status_code == 400 and r.json()["error"]["code"] == "bad_request"


def test_auth_enforced_when_key_set(client, monkeypatch):
    from signalcraft import config
    monkeypatch.setattr(config.settings, "api_key", "secret")
    assert client.get("/api/profile").status_code == 401
    assert client.get("/api/profile", headers={"X-API-Key": "nope"}).status_code == 401
    assert client.get("/api/profile", headers={"X-API-Key": "secret"}).status_code == 200


def test_signup_login_me_logout(client):
    s = client.post("/api/auth/signup", json={
        "name": "Sankiyy", "email": "demo@example.com", "password": "password123"}).json()
    assert s["user"]["onboarding_status"] == "IN_PROGRESS"
    token = s["token"]
    me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"}).json()
    assert me["user"]["email"] == "demo@example.com"
    assert client.post("/api/auth/signup", json={
        "name": "X", "email": "demo@example.com", "password": "password123"}).status_code == 400
    assert client.post("/api/auth/login", json={
        "email": "demo@example.com", "password": "wrongpass1"}).status_code == 400
    assert client.get("/api/auth/me", headers={"Authorization": "Bearer nope"}).status_code == 401
    assert client.post("/api/auth/logout",
                       headers={"Authorization": f"Bearer {token}"}).status_code == 200
    assert client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"}).status_code == 401


def test_onboarding_journey(client):
    s = client.post("/api/auth/signup", json={
        "name": "Creator", "email": "j@example.com", "password": "password123"}).json()
    h = {"Authorization": f"Bearer {s['token']}"}
    st = client.get("/api/onboarding/status", headers=h).json()
    assert st["status"] == "IN_PROGRESS" and not st["niche_set"]
    assert client.post("/api/onboarding/complete", headers=h).status_code == 400
    assert client.post("/api/onboarding", headers=h, json={"bogus": 1}).status_code == 422
    r = client.post("/api/onboarding", headers=h, json={
        "name": "Sankiyy", "role": "AI student", "niche": "AI + Data Engineering",
        "topics": ["AI agents", "LLMs"], "audience": "Developers",
        "audience_segments": ["Students"], "goals": ["Personal branding"],
        "platforms": ["LinkedIn", "X"], "tone": "Technical + simple",
        "formats": ["Tutorial"], "frequency": "3-5 / week"}).json()
    assert r["niche_set"] and r["name_set"]
    done = client.post("/api/onboarding/complete", headers=h).json()
    assert done["status"] == "COMPLETED"
    assert done["summary"]["niche"] == "AI + Data Engineering"
    assert done["built"]["opportunities"] >= 1
    prefs = client.get("/api/preferences", headers=h).json()
    assert prefs["frequency"] == "3-5 / week" and prefs["formats"] == ["Tutorial"]
    ctx = client.get("/api/context", headers=h).json()
    assert ctx["niche"] == "AI + Data Engineering" and "Students" in ctx["audience_segments"]
    assert "AI agents" in ctx["tracked_topics"]


def test_preferences_validation(client):
    assert client.put("/api/preferences", json={"creativity": 0.2}).json()["creativity"] == 0.2
    assert client.put("/api/preferences", json={"creativity": 9}).json()["creativity"] == 1.0


def test_google_boundary_and_status_flow(client, monkeypatch):
    from signalcraft import config
    st = client.get("/api/auth/google/status").json()
    assert st["configured"] is False
    assert client.get("/api/auth/google/start").status_code == 501
    monkeypatch.setattr(config.settings, "google_client_id", "test-id")
    monkeypatch.setattr(config.settings, "google_client_secret", "test-secret")
    assert client.get("/api/auth/google/status").json()["configured"] is True
    r = client.get("/api/auth/google/start", follow_redirects=False)
    assert r.status_code == 302 and "accounts.google.com" in r.headers["location"]
    bad = client.get("/api/auth/google/callback?code=x&state=bad", follow_redirects=False)
    assert bad.status_code == 302 and "/login?error=" in bad.headers["location"]
    assert client.get("/api/trends", params={"sort": "rising"}).status_code == 200
    assert client.get("/api/trends", params={"sort": "latest"}).status_code == 200
    client.post("/api/research", json={"limit": 5, "use_live": False})
    opps = client.get("/api/opportunities", params={"refresh": True}).json()
    gen = client.post("/api/content/generate",
                      json={"opportunity_id": opps[0]["id"], "platform": "Blog"}).json()
    assert gen["persisted"] is False
    cid = client.post("/api/content/save", json={
        "opportunity_id": opps[0]["id"], "platform": "Blog",
        "title": gen["content"]["title"], "body": gen["content"]["body"],
        "hook": gen["content"]["hook"], "brief": gen["brief"]}).json()["content"]["id"]
    assert client.put(f"/api/content/{cid}/status", json={"status": "published"}).json()["status"] == "published"
    assert client.put(f"/api/content/{cid}/status", json={"status": "nope"}).status_code == 400


def test_content_lifecycle_and_newsletter(client):
    client.post("/api/research", json={"limit": 5, "use_live": False})
    opps = client.get("/api/opportunities", params={"refresh": True}).json()
    gen = client.post("/api/content/generate",
                      json={"opportunity_id": opps[0]["id"], "platform": "Newsletter"}).json()
    assert "Subject:" in gen["content"]["body"]
    assert gen["brief"].get("format") in ("", "Insight + example + takeaway")
    cid = client.post("/api/content/save", json={
        "opportunity_id": opps[0]["id"], "platform": "Newsletter",
        "title": gen["content"]["title"], "body": gen["content"]["body"],
        "format": "Tutorial"}).json()["content"]["id"]
    row = client.get(f"/api/content/{cid}").json()
    assert row["format"] == "Tutorial"
    by_format = client.get("/api/analytics").json()["by_format"]
    assert any(f.get("format") == "Tutorial" for f in by_format)
    dup = client.post(f"/api/content/{cid}/duplicate").json()["content"]
    assert dup["id"] != cid and dup["status"] == "draft"
    assert client.delete(f"/api/content/{cid}").json()["ok"] is True
    assert client.get(f"/api/content/{cid}").status_code == 400
    assert client.delete("/api/content/9999").status_code == 400
    v2 = client.post("/api/content/revise", json={"content_id": dup["id"]}).json()
    assert v2["version"] == 2
    rst = client.post(f"/api/content/{dup['id']}/restore", json={"version": 1}).json()
    assert rst["version"] == 3 and rst["restored_from"] == 1
    assert client.post(f"/api/content/{dup['id']}/restore", json={"version": 99}).status_code == 400


def test_calendar_edit_and_research_list(client):
    client.post("/api/research", json={"limit": 5, "use_live": False})
    created = client.post("/api/calendar", json={
        "platform": "LinkedIn", "scheduled_for": "2026-10-01 10:00",
        "notes": "launch post"}).json()
    eid = created["id"]
    upd = client.put(f"/api/calendar/{eid}", json={"status": "scheduled"}).json()
    assert upd["status"] == "scheduled"
    assert client.put(f"/api/calendar/{eid}", json={"status": "bogus"}).status_code == 400
    dup = client.post(f"/api/calendar/{eid}/duplicate").json()
    assert dup["id"] != eid and dup["status"] == "draft"
    docs = client.get("/api/research", params={"limit": 5}).json()["documents"]
    assert len(docs) >= 1 and docs[0]["title"]
    found = client.get("/api/research", params={"query": "zz-no-such-topic"}).json()["documents"]
    assert found == []
