"""OAuth user + state logic (offline; Google HTTP is never touched)."""
import pytest

from signalcraft import auth, oauth


def test_oauth_create_link_idempotent(tmp_db):
    u1 = auth.create_oauth_user("g@example.com", "G User", "google", "sub-1")
    assert u1["onboarding_status"] == "IN_PROGRESS"
    # same sub returns same user
    assert auth.create_oauth_user("other@example.com", "X", "google", "sub-1")["id"] == u1["id"]
    # password login impossible for oauth-only accounts
    with pytest.raises(ValueError):
        auth.authenticate("g@example.com", "anything12")


def test_oauth_links_existing_email(tmp_db):
    auth.create_user("Plain", "p@example.com", "password123")
    linked = auth.create_oauth_user("p@example.com", "Plain", "google", "sub-9")
    assert linked["email"] == "p@example.com"
    # password still works after linking
    assert auth.authenticate("p@example.com", "password123")["id"] == linked["id"]


def test_oauth_state_single_use_and_invalid(tmp_db, monkeypatch):
    from signalcraft import config
    monkeypatch.setattr(config.settings, "google_client_id", "t")
    monkeypatch.setattr(config.settings, "google_client_secret", "s")
    url = oauth.start_login()
    assert "accounts.google.com" in url
    state = url.split("state=")[1].split("&")[0]
    with pytest.raises(ValueError):
        oauth.handle_callback("", state)  # missing code
    with pytest.raises(ValueError):
        oauth.handle_callback("c", "nope")  # unknown state


def test_oauth_unconfigured(monkeypatch):
    from signalcraft import config
    monkeypatch.setattr(config.settings, "google_client_id", "")
    monkeypatch.setattr(config.settings, "google_client_secret", "")
    assert oauth.is_configured() is False
    with pytest.raises(ValueError):
        oauth.start_login()
