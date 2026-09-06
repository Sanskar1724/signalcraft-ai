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
    db.init_db(tmp_path / "api.db")
    from apps.api.app.main import app
    from fastapi.testclient import TestClient
    with TestClient(app) as c:
        yield c


def test_health(client):
    r = client.get("/api/health")
    assert r.status_code == 200 and r.json()["ok"] is True
    assert r.headers.get("X-Request-ID")


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
    cid = gen["content"]["id"]
    assert gen["brief"]["topic"] == opps[0]["topic"]
    crit = client.post("/api/content/critique",
                       json={"body": gen["content"]["body"], "platform": "LinkedIn"}).json()
    assert crit["overall"] >= 0
    rev = client.post("/api/content/revise", json={"content_id": cid}).json()
    assert rev["version"] == 2
    items = client.get("/api/content").json()
    assert len(items) >= 1
    detail = client.get(f"/api/content/{cid}").json()
    assert len(detail["versions"]) == 2 and detail["brief"]
    perf = client.post(f"/api/content/{cid}/performance",
                       json={"impressions": 1000, "likes": 60}).json()
    assert perf["engagement_rate"] == 6.0
    assert client.get("/api/analytics").json()["posts"] >= 1
    assert client.get("/api/insights").json()["insights"]
    chat = client.post("/api/agent/chat", json={"message": "What should I post today?"}).json()
    assert "Observed fact" in chat["answer"] and chat["request_id"]
    assert client.get("/api/debug/llm").json()["usage"]


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
