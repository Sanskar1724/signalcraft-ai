"""LLM gateway (§21): generate / structured_generate / embed + usage tracking.

Provider order: explicit > OpenRouter (initial live provider) > OpenAI-compatible
> Mock (offline default). §34 routing: cheap/small models for classification,
extraction, tagging, simple summarization; stronger models for strategy,
reasoning, final content, critique.
"""
from __future__ import annotations

import hashlib
import json
import math
import time
from typing import Any

from ..config import settings
from ..observability import log
from .providers import (BaseProvider, MockProvider, OpenAICompatibleProvider,
                        OpenRouterProvider)

# Task routing: simple tasks prefer cheap/fast, hard tasks prefer stronger.
CHEAP_TASKS = {"classification", "extraction", "tagging", "summarization"}
STRONG_TASKS = {"strategy", "generation", "critique", "research synthesis"}
TASK_MODEL_HINTS = {t: "fast" for t in CHEAP_TASKS} | {t: "strong" for t in STRONG_TASKS} | {
    "research synthesis": "balanced", "critique": "balanced", "embedding": "local",
}


class LLMGateway:
    def __init__(self, provider: BaseProvider | None = None):
        if provider is not None:
            self.provider = provider
        elif settings.openrouter_api_key:
            self.provider = OpenRouterProvider(
                settings.openrouter_api_key, settings.openrouter_base_url,
                model=settings.strong_model if settings.strong_model != "mock"
                else "openai/gpt-4o-mini",
            )
        elif settings.openai_api_key:
            self.provider = OpenAICompatibleProvider(
                settings.openai_api_key, settings.openai_base_url,
                model="gpt-4o-mini",
            )
        else:
            self.provider = MockProvider()

    def _model_for(self, task: str) -> str:
        hint = TASK_MODEL_HINTS.get(task, "balanced")
        if hint == "fast":
            return settings.cheap_model
        if hint == "strong":
            return settings.strong_model
        return settings.primary_model

    def generate(self, prompt: str, task: str = "generation", max_tokens: int = 800) -> str:
        t0 = time.time()
        try:
            result = self.provider.generate(prompt, task=task, max_tokens=max_tokens)
            self._track(result.provider, result.model, task, result.latency_ms,
                        result.prompt_tokens, result.completion_tokens, True,
                        result.cost_usd)
            return result.text
        except Exception as e:  # §32 fallback: never crash the app
            log.warning("LLM provider failed (%s), falling back to mock", e)
            fb = MockProvider().generate(prompt, task=task, max_tokens=max_tokens)
            latency = int((time.time() - t0) * 1000)
            self._track("mock-fallback", "mock-1", task, latency,
                        len(prompt) // 4, len(fb.text) // 4, False)
            return fb.text

    def structured_generate(self, prompt: str, task: str = "extraction") -> dict[str, Any]:
        raw = self.generate(prompt + "\n\nRespond with JSON only.", task=task)
        try:
            start, end = raw.find("{"), raw.rfind("}")
            if start != -1 and end != -1:
                return json.loads(raw[start:end + 1])
        except Exception:
            pass
        return {"raw": raw}

    def embed(self, text: str, dim: int = 64) -> list[float]:
        """Local hash embedding (offline, deterministic). Real embeddings can plug in later."""
        vec = [0.0] * dim
        for tok in text.lower().split():
            h = int(hashlib.md5(tok.encode()).hexdigest(), 16)
            vec[h % dim] += 1.0
        norm = math.sqrt(sum(v * v for v in vec)) or 1.0
        return [v / norm for v in vec]

    def _track(self, provider: str, model: str, task: str, latency_ms: int,
               pt: int, ct: int, success: bool, cost_usd: float = 0.0) -> None:
        try:
            from ..db import get_conn, new_uuid
            conn = get_conn()
            try:
                conn.execute(
                    "INSERT INTO llm_requests (uuid, provider, model, task, latency_ms,"
                    " prompt_tokens, completion_tokens, cost_usd, success)"
                    " VALUES (?,?,?,?,?,?,?,?,?)",
                    (new_uuid(), provider, model, task, latency_ms, pt, ct,
                     cost_usd, int(success)),
                )
                conn.commit()
            finally:
                conn.close()
        except Exception as e:
            log.warning("llm tracking failed: %s", e)
