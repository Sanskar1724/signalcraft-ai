"""Google OAuth login (§27 real boundary): authorization-code flow over plain
HTTPS (no extra dependencies). State nonces are single-use with a 10-min TTL.
"""
from __future__ import annotations

import secrets
import urllib.parse
from datetime import datetime, timedelta, timezone

import requests

from . import auth as _auth
from .config import settings
from .db import get_conn

__all__ = ["is_configured", "redirect_uri", "start_login", "handle_callback"]

AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"
USERINFO_URL = "https://openidconnect.googleapis.com/v1/userinfo"
STATE_TTL_S = 600


def is_configured() -> bool:
    return bool(settings.google_client_id and settings.google_client_secret)


def redirect_uri() -> str:
    return settings.backend_url.rstrip("/") + "/api/auth/google/callback"


def start_login() -> str:
    """Create a one-time state and return the Google authorize URL."""
    if not is_configured():
        raise ValueError("google_oauth_not_configured")
    state = secrets.token_urlsafe(32)
    conn = get_conn()
    try:
        conn.execute("INSERT INTO oauth_states (state) VALUES (?)", (state,))
        conn.execute(
            "DELETE FROM oauth_states WHERE created_at < datetime('now', '-10 minutes')")
        conn.commit()
    finally:
        conn.close()
    params = {
        "client_id": settings.google_client_id,
        "redirect_uri": redirect_uri(),
        "response_type": "code",
        "scope": "openid email profile",
        "state": state,
        "prompt": "select_account",
    }
    return AUTH_URL + "?" + urllib.parse.urlencode(params)


def _consume_state(state: str) -> None:
    conn = get_conn()
    try:
        row = conn.execute("SELECT created_at FROM oauth_states WHERE state=?",
                           (state,)).fetchone()
        conn.execute("DELETE FROM oauth_states WHERE state=?", (state,))
        conn.commit()
    finally:
        conn.close()
    if row is None:
        raise ValueError("invalid or reused oauth state")
    try:
        created = datetime.strptime(row["created_at"], "%Y-%m-%d %H:%M:%S").replace(
            tzinfo=timezone.utc)
    except Exception:
        raise ValueError("invalid oauth state timestamp")
    if datetime.now(timezone.utc) - created > timedelta(seconds=STATE_TTL_S):
        raise ValueError("expired oauth state")


def handle_callback(code: str, state: str) -> tuple[dict, str]:
    """Exchange code → verify email → find-or-create user → session token."""
    if not code or not state:
        raise ValueError("missing code or state")
    _consume_state(state)
    try:
        resp = requests.post(TOKEN_URL, data={
            "code": code, "client_id": settings.google_client_id,
            "client_secret": settings.google_client_secret,
            "redirect_uri": redirect_uri(), "grant_type": "authorization_code",
        }, timeout=20)
        resp.raise_for_status()
        access = resp.json().get("access_token")
        if not access:
            raise ValueError("no access token in google response")
        me = requests.get(USERINFO_URL, headers={"Authorization": f"Bearer {access}"},
                          timeout=20)
        me.raise_for_status()
        info = me.json()
    except ValueError:
        raise
    except Exception as e:
        raise ValueError(f"google token exchange failed: {e}")
    if not info.get("email_verified"):
        raise ValueError("google email not verified")
    email = str(info.get("email", "")).strip().lower()
    if not email:
        raise ValueError("google account has no email")
    user = _auth.create_oauth_user(email, str(info.get("name", "")), "google",
                                   str(info.get("sub", "")))
    return user, _auth.create_session(user["id"])
