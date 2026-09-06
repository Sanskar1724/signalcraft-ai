"""Use-case services: thin orchestration over domain modules (§4)."""
from __future__ import annotations

import json

from signalcraft import analytics, calendar, jobs
from signalcraft import memory as _memory
from signalcraft import opportunities as _opps
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

__all__ = ["profile", "research", "trend", "opportunity", "content", "agent"]


class profile:
    @staticmethod
    def get(user_id: int = 1) -> dict:
        p = _profiles.get_profile(user_id)
        return {k: getattr(p, k) for k in (
            "user_id", "niche", "expertise", "expertise_level", "audience", "goals",
            "platforms", "writing_style", "tone", "topics", "avoid_topics",
            "style_notes", "content_preferences", "posting_preferences")}

    @staticmethod
    def update(user_id: int = 1, **fields) -> dict:
        fields = {k: v for k, v in fields.items() if v is not None}
        if fields:
            _profiles.update_profile(user_id, **fields)
        return profile.get(user_id)


class research:
    @staticmethod
    def run(query: str = "", limit: int = 20, use_live: bool = True, user_id: int = 1) -> dict:
        return jobs.run_refresh(user_id=user_id, limit=limit, use_live=use_live)

    @staticmethod
    def recent(user_id: int = 1, limit: int = 30, offset: int = 0) -> list[dict]:
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
    def list(user_id: int = 1, limit: int = 20, offset: int = 0) -> list[dict]:
        return _opps.list_opportunities(user_id, limit, offset)


class content:
    @staticmethod
    def generate(opportunity_id: int, platform: str = "LinkedIn", user_id: int = 1) -> dict:
        res = _generate(opportunity_id, platform=platform, user_id=user_id)
        return {"content": res["content"], "critique": res["critique"],
                "brief": res["brief"].model_dump()}

    @staticmethod
    def critique(body: str, platform: str = "LinkedIn", topic: str = "") -> dict:
        return _critique(body, platform=platform, topic=topic)

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
        new_body = (detail["body"] + f"\n\nRefinement: {fix[:800]}")[:6000]
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
    def log_performance(content_id: int, user_id: int = 1, **metrics) -> dict:
        row = analytics.record_performance(content_id, **metrics)
        _memory.learn_from_performance(user_id)
        return row


class agent:
    @staticmethod
    def chat(message: str, user_id: int = 1) -> dict:
        from signalcraft.agent import run
        from ..api.deps import current_request_id
        out = run(message, user_id=user_id)
        out["request_id"] = current_request_id()
        return out

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
