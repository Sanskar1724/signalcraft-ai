"""Authentication (§31): pbkdf2 passwords (stdlib) + opaque session tokens.

Multi-user capable; single-user dev fallback lives in the API layer, not here.
"""
from __future__ import annotations

import hashlib
import hmac
import secrets

from .db import get_conn, new_uuid

__all__ = [
    "ONBOARDING_STATES",
    "authenticate",
    "change_password",
    "create_oauth_user",
    "create_session",
    "create_user",
    "destroy_session",
    "get_user",
    "get_user_by_token",
    "hash_password",
    "set_onboarding_status",
    "verify_password",
]

ONBOARDING_STATES = ("NOT_STARTED", "IN_PROGRESS", "COMPLETED")
_ITERS = 200_000


def hash_password(password: str) -> str:
    if len(password) < 8:
        raise ValueError("password must be at least 8 characters")
    salt = secrets.token_hex(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), _ITERS)
    return f"pbkdf2${_ITERS}${salt}${dk.hex()}"


def verify_password(password: str, hashed: str) -> bool:
    try:
        _, iters, salt, expect = hashed.split("$")
        dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), int(iters))
        return hmac.compare_digest(dk.hex(), expect)
    except Exception:
        return False


def create_user(name: str, email: str, password: str) -> dict:
    email = email.strip().lower()
    if not name.strip():
        raise ValueError("name is required")
    if "@" not in email:
        raise ValueError("valid email is required")
    conn = get_conn()
    try:
        if conn.execute("SELECT id FROM users WHERE email=?", (email,)).fetchone():
            raise ValueError("email already registered")
        cur = conn.execute(
            "INSERT INTO users (uuid, name, email, password_hash, onboarding_status)"
            " VALUES (?,?,?,?, 'IN_PROGRESS')",
            (new_uuid(), name.strip(), email, hash_password(password)),
        )
        uid = cur.lastrowid
        conn.execute("INSERT OR IGNORE INTO profiles (uuid, user_id) VALUES (?, ?)",
                     (new_uuid(), uid))
        conn.execute("INSERT OR IGNORE INTO preferences (uuid, user_id) VALUES (?, ?)",
                     (new_uuid(), uid))
        conn.commit()
        return get_user(uid)
    finally:
        conn.close()


def authenticate(email: str, password: str) -> dict:
    conn = get_conn()
    try:
        row = conn.execute("SELECT * FROM users WHERE email=?", (email.strip().lower(),)).fetchone()
        if row is None or not row["password_hash"] \
                or not verify_password(password, row["password_hash"]):
            raise ValueError("invalid email or password")
        return dict(row)
    finally:
        conn.close()


def create_session(user_id: int) -> str:
    token = secrets.token_hex(32)
    conn = get_conn()
    try:
        conn.execute("INSERT INTO sessions (uuid, user_id, token) VALUES (?,?,?)",
                     (new_uuid(), user_id, token))
        conn.commit()
        return token
    finally:
        conn.close()


def get_user_by_token(token: str) -> dict | None:
    conn = get_conn()
    try:
        row = conn.execute(
            "SELECT u.* FROM users u JOIN sessions s ON s.user_id=u.id WHERE s.token=?",
            (token,)).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()

def destroy_session(token: str) -> None:
    conn = get_conn()
    try:
        conn.execute("DELETE FROM sessions WHERE token=?", (token,))
        conn.commit()
    finally:
        conn.close()

def change_password(user_id: int, current: str, new: str) -> None:
    conn = get_conn()
    try:
        row = conn.execute("SELECT password_hash FROM users WHERE id=?", (user_id,)).fetchone()
        if row is None or not row["password_hash"] \
                or not verify_password(current, row["password_hash"]):
            raise ValueError("current password is incorrect")
        conn.execute("UPDATE users SET password_hash=? WHERE id=?",
                     (hash_password(new), user_id))
        conn.execute("DELETE FROM sessions WHERE user_id=?", (user_id,))
        conn.commit()
    finally:
        conn.close()


def create_oauth_user(email: str, name: str = "", provider: str = "google",
                      sub: str = "") -> dict:
    """Find-or-create for OAuth logins. Matches provider+sub first (stable),
    then links by verified email, else creates an OAuth-only account
    (empty password_hash → password login impossible)."""
    email = email.strip().lower()
    if "@" not in email:
        raise ValueError("oauth account has no valid email")
    conn = get_conn()
    try:
        row = None
        if sub:
            row = conn.execute(
                "SELECT id FROM users WHERE provider=? AND provider_sub=?",
                (provider, sub)).fetchone()
        if row is None:
            row = conn.execute("SELECT id FROM users WHERE email=?", (email,)).fetchone()
            if row is not None:
                conn.execute("UPDATE users SET provider=?, provider_sub=? WHERE id=?",
                             (provider, sub, row["id"]))
                conn.commit()
        if row is None:
            cur = conn.execute(
                "INSERT INTO users (uuid, name, email, password_hash, provider,"
                " provider_sub, onboarding_status)"
                " VALUES (?,?,?,?,?,?,'IN_PROGRESS')",
                (new_uuid(), (name or email.split("@")[0]).strip(),
                 email, "", provider, sub),
            )
            uid = cur.lastrowid
            conn.execute("INSERT OR IGNORE INTO profiles (uuid, user_id) VALUES (?, ?)",
                         (new_uuid(), uid))
            conn.execute("INSERT OR IGNORE INTO preferences (uuid, user_id) VALUES (?, ?)",
                         (new_uuid(), uid))
            conn.commit()
            row = {"id": uid}
        uid = row["id"]
    finally:
        conn.close()
    return get_user(uid)


def get_user(user_id: int) -> dict:
    conn = get_conn()
    try:
        row = conn.execute("SELECT id, uuid, name, email, onboarding_status, created_at"
                           " FROM users WHERE id=?", (user_id,)).fetchone()
        if row is None:
            raise ValueError(f"user {user_id} not found")
        return dict(row)
    finally:
        conn.close()


def set_onboarding_status(user_id: int, status: str) -> dict:
    if status not in ONBOARDING_STATES:
        raise ValueError(f"invalid status: {status}")
    conn = get_conn()
    try:
        conn.execute("UPDATE users SET onboarding_status=? WHERE id=?", (status, user_id))
        conn.commit()
        return get_user(user_id)
    finally:
        conn.close()
