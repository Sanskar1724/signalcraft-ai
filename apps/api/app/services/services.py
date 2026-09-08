"""Use-case services: thin orchestration over domain modules (§4)."""
from __future__ import annotations

import json

from signalcraft import analytics, calendar, jobs
from signalcraft import auth as _auth
from signalcraft import memory as _memory
from signalcraft import onboarding as _onboarding
from signalcraft import opportunities as _opps
from signalcraft import personalization as _personalization
from signalcraft import preferences as _prefs
from signalcraft import profiles as _profiles
from signalcraft import trends as _trends
from signalcraft.content import critique as _critique
from signalcraft.content import generate_content as _generate
from signalcraft.content import list_content
from signalcraft.content import validate as _validate
from signalcraft.llm import LLMGateway
from signalcraft.llm.prompts import render
from signalcraft.research import list_recent

from ..repositories.content import get_content_detail

__all__ = ["profile", "research", "trend", "opportunity", "content", "agent",
           "identity", "onboarding", "preferences", "context"]


class identity:
    @staticmethod
    def signup(name: str, email: str, password: str) -> dict:
        user = _auth.create_user(name, email, password)
        return {"user": user, "token": _auth.create_session(user["id"])}

    @staticmethod
    def login(email: str, password: str) -> dict:
        user = _auth.authenticate(email, password)
        return {"user": user, "token": _auth.create_session(user["id"])}

    @staticmethod
    def logout(token: str) -> dict:
        _auth.destroy_session(token)
        return {"ok": True}

    @staticmethod
    def password(user_id: int, current: str, new: str) -> dict:
        _auth.change_password(user_id, current, new)
        return {"ok": True, "note": "all other sessions were signed out; log in again"}

    @staticmethod
    def me(user_id: int) -> dict:
        user = _auth.get_user(user_id)
        profile = _profiles.get_profile(user_id)
        return {"user": user, "profile_name": profile.name,
                "onboarding_status": user["onboarding_status"]}


class onboarding:
    @staticmethod
    def status(user_id: int = 1) -> dict:
        return _onboarding.get_status(user_id)

    @staticmethod
    def apply(user_id: int = 1, **payload) -> dict:
        return _onboarding.apply_step(user_id, **payload)

    @staticmethod
    def complete(user_id: int = 1) -> dict:
        return _onboarding.complete(user_id)


class preferences:
    @staticmethod
    def get(user_id: int = 1) -> dict:
        return _prefs.get_preferences(user_id)

    @staticmethod
    def update(user_id: int = 1, **fields) -> dict:
        return _prefs.update_preferences(user_id, **fields)


class context:
    @staticmethod
    def get(user_id: int = 1) -> dict:
        return _personalization.build_context(user_id)


class profile:
    @staticmethod
    def get(user_id: int = 1) -> dict:
        p = _profiles.get_profile(user_id)
        return {k: getattr(p, k) for k in (
            "user_id", "name", "role", "bio", "location",
            "niche", "expertise", "expertise_level", "audience", "goals",
            "platforms", "writing_style", "tone", "topics", "avoid_topics",
            "style_notes", "content_preferences", "posting_preferences")}

    @staticmethod
    def update(user_id: int = 1, **fields) -> dict:
        fields = {k: v for k, v in fields.items() if v is not None}
        if "name" in fields:
            from signalcraft.db import get_conn
            conn = get_conn()
            try:
                conn.execute("UPDATE users SET name=? WHERE id=?",
                             (str(fields.pop("name")).strip(), user_id))
                conn.commit()
            finally:
                conn.close()
        if fields:
            _profiles.update_profile(user_id, **fields)
        return profile.get(user_id)


class research:
    @staticmethod
    def run(query: str = "", limit: int = 20, use_live: bool = True, user_id: int = 1) -> dict:
        return jobs.run_refresh(user_id=user_id, limit=limit, use_live=use_live)

    @staticmethod
    def documents(user_id: int = 1, query: str = "", limit: int = 30,
                  offset: int = 0) -> list[dict]:
        from signalcraft.research import list_recent, search
        if query:
            return search(user_id, query, limit, offset)
        return list_recent(user_id, limit, offset)


class trend:
    @staticmethod
    def list(user_id: int = 1, top_n: int = 10) -> list[dict]:
        return _trends.detect_trends(user_id, top_n)


class opportunity:
    @staticmethod
    def rank(user_id: int = 1, top_n: int = 8) -> list[dict]:
        return _opps.build_opportunities(user_id, top_n)

    @staticmethod
    def dismiss(user_id: int = 1, opportunity_id: int = 0) -> dict:
        from signalcraft import memory as _mem
        from signalcraft.db import get_conn
        conn = get_conn()
        try:
            row = conn.execute("SELECT * FROM content_opportunities WHERE id=? AND user_id=?",
                               (opportunity_id, user_id)).fetchone()
            if row is None:
                raise ValueError(f"opportunity {opportunity_id} not found")
            conn.execute("UPDATE content_opportunities SET status='dismissed' WHERE id=?",
                         (opportunity_id,))
            conn.commit()
            topic = row["topic"]
        finally:
            conn.close()
        # Dismissal is feedback: weak-topic memory demotes similar ideas (§10).
        _mem.remember(user_id, "weak_topic", topic.lower()[:80], "dismissed by creator", 0.7)
        return {"ok": True, "opportunity_id": opportunity_id}

    @staticmethod
    def list(user_id: int = 1, limit: int = 20, offset: int = 0) -> list[dict]:
        return _opps.list_opportunities(user_id, limit, offset)


class content:
    @staticmethod
    def generate(opportunity_id: int, platform: str = "LinkedIn", user_id: int = 1,
                 tone: str | None = None, length: str = "medium",
                 style_match: bool = True, grounded: bool = True) -> dict:
        # §13: preview only — explicit Save persists.
        res = _generate(opportunity_id, platform=platform, user_id=user_id,
                        tone=tone, length=length, style_match=style_match,
                        grounded=grounded, persist=False)
        return {"content": res["content"], "critique": res["critique"],
                "brief": res["brief"].model_dump(), "persisted": False}

    @staticmethod
    def save(user_id: int = 1, opportunity_id: int | None = None,
             platform: str = "LinkedIn", title: str = "", body: str = "",
             hook: str = "", cta: str = "", brief: dict | None = None) -> dict:
        from signalcraft.content import save_draft
        return save_draft(user_id, platform, title, body, hook, cta,
                          opportunity_id, brief)

    @staticmethod
    def remove(user_id: int = 1, content_id: int = 0) -> dict:
        from signalcraft.content import remove_content
        return remove_content(content_id, user_id)

    @staticmethod
    def duplicate(user_id: int = 1, content_id: int = 0) -> dict:
        from signalcraft.content import duplicate_content
        return duplicate_content(content_id, user_id)

    @staticmethod
    def critique(body: str, platform: str = "LinkedIn", topic: str = "") -> dict:
        return _critique(body, platform=platform, topic=topic)

    @staticmethod
    def improve_preview(body: str, platform: str = "LinkedIn") -> dict:
        """Improve a preview WITHOUT storing (§13: improve before save)."""
        from signalcraft.content.sanitize import scrub as _scrub
        check = _validate(body, platform=platform, grounded=False)
        if not check["ok"]:
            raise ValueError(f"cannot improve invalid draft: {check['errors']}")
        crit = _critique(body, platform=platform)
        gateway = LLMGateway()
        fix = gateway.generate(
            render("content_revision", platform=platform,
                   issues=crit["suggestion"], draft=body[:1500]),
            task="generation", max_tokens=500).strip()
        new_body = _scrub(fix[:2000])
        final = _critique(new_body, platform=platform)
        return {"body": new_body, "critique": final,
                "previous_score": crit["overall"]}

    @staticmethod
    def revise(content_id: int, user_id: int = 1) -> dict:
        from signalcraft.db import get_conn, new_uuid
        detail = get_content_detail(content_id, user_id)
        crit = _critique(detail["body"], platform=detail["platform"])
        gateway = LLMGateway()
        fix = gateway.generate(
            render("content_revision", platform=detail["platform"],
                   issues=crit["suggestion"], draft=detail["body"][:1500]),
            task="generation", max_tokens=500).strip()
        if fix.startswith("[Mock draft"):
            fix = fix.split("]", 1)[-1].strip()
        from signalcraft.content.sanitize import scrub as _scrub
        new_body = _scrub(detail["body"] + f"\n\nRefinement: {fix[:800]}")[:6000]
        check = _validate(new_body, platform=detail["platform"])
        if not check["ok"]:
            raise ValueError(f"revision failed validation: {check['errors']}")
        final = _critique(new_body, platform=detail["platform"])
        conn = get_conn()
        try:
            cur_version = max([v["version"] for v in detail["versions"]] or [1])
            conn.execute(
                "UPDATE content SET body=?, quality_score=? WHERE id=?",
                (new_body, final["overall"], content_id))
            conn.execute(
                "INSERT INTO content_versions (uuid, content_id, version, brief, body,"
                " critique, score) VALUES (?,?,?,?,?,?,?)",
                (new_uuid(), content_id, cur_version + 1,
                 json.dumps(detail.get("brief") or {}), new_body,
                 json.dumps(final), final["overall"]))
            conn.commit()
        finally:
            conn.close()
        return {"content_id": content_id, "version": cur_version + 1,
                "critique": final, "body": new_body}

    @staticmethod
    def history(user_id: int = 1, limit: int = 50, offset: int = 0,
                platform: str | None = None) -> list[dict]:
        return list_content(user_id, limit, offset, platform)

    @staticmethod
    def set_status(content_id: int, user_id: int = 1, status: str = "draft") -> dict:
        if status not in {"draft", "ready", "published", "archived"}:
            raise ValueError(f"invalid status: {status}")
        from signalcraft.db import get_conn
        from ..repositories.content import get_content_detail
        get_content_detail(content_id, user_id)  # 404-style guard
        conn = get_conn()
        try:
            conn.execute("UPDATE content SET status=? WHERE id=? AND user_id=?",
                         (status, content_id, user_id))
            conn.commit()
        finally:
            conn.close()
        return get_content_detail(content_id, user_id)

    @staticmethod
    def log_performance(content_id: int, user_id: int = 1, **metrics) -> dict:
        row = analytics.record_performance(content_id, **metrics)
        _memory.learn_from_performance(user_id)
        return row


class agent:
    @staticmethod
    def chat(message: str, user_id: int = 1) -> dict:
        from signalcraft.agent import list_opportunities_for_actions, run
        from signalcraft.contracts import AgentResult
        from ..api.deps import current_request_id
        out = run(message, user_id=user_id)
        out["request_id"] = current_request_id()
        out["actions"] = list_opportunities_for_actions(out.get("intent", ""), user_id)
        checked = AgentResult(**{k: out.get(k) for k in
                                 ("answer", "intent", "request_id", "trace")}).model_dump()
        checked["actions"] = out["actions"]
        return checked

    @staticmethod
    def learn(user_id: int = 1) -> dict:
        notes = _memory.learn_from_performance(user_id)
        return {"learned": notes}

    @staticmethod
    def memories(user_id: int = 1, limit: int = 50) -> list[dict]:
        return _memory.recall(user_id, limit=limit)

    @staticmethod
    def calendar(user_id: int = 1, limit: int = 30) -> list[dict]:
        return calendar.upcoming(user_id, limit)

    @staticmethod
    def schedule(user_id: int = 1, **fields) -> dict:
        return calendar.schedule(user_id, **fields)

    @staticmethod
    def reschedule(user_id: int = 1, entry_id: int = 0, **fields) -> dict:
        return calendar.update_entry(entry_id, user_id, **fields)

    @staticmethod
    def duplicate_entry(user_id: int = 1, entry_id: int = 0) -> dict:
        return calendar.duplicate_entry(entry_id, user_id)
