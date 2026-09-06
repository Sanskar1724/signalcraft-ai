"""LLM provider abstraction. Mock works offline; OpenAI-compatible is optional."""
from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass

import requests


@dataclass
class LLMResult:
    text: str
    provider: str
    model: str
    latency_ms: int
    prompt_tokens: int
    completion_tokens: int


class BaseProvider:
    name = "base"

    def generate(self, prompt: str, task: str = "generation", max_tokens: int = 800) -> LLMResult:
        raise NotImplementedError


def _tokens(s: str) -> int:
    return max(1, len(s) // 4)


class MockProvider(BaseProvider):
    """Deterministic offline provider. Never calls network. Good for tests/dev."""

    name = "mock"

    def generate(self, prompt: str, task: str = "generation", max_tokens: int = 800) -> LLMResult:
        t0 = time.time()
        digest = hashlib.md5(f"{task}:{prompt}".encode()).hexdigest()[:8]
        # Task-aware stubs — deterministic, clearly marked as draft assistance.
        if task == "strategy":
            text = (
                f"[Mock strategy {digest}] Goal: pick one sharp angle. "
                f"Structure: hook -> 3 insights -> proof -> CTA. "
                f"Keep it specific, avoid generic hype. Prompt context: {prompt[:220]}"
            )
        elif task == "critique":
            text = json.dumps({
                "relevance": 7, "clarity": 7, "hook": 6, "platform_fit": 7,
                "tone": 7, "evidence": 5, "issues": ["add concrete example", "tighten hook"],
                "suggestion": "Strengthen opening line and add one data point.",
                "mock_id": digest,
            })
        elif task == "classification":
            text = json.dumps({"label": "relevant", "confidence": 0.6, "mock_id": digest})
        else:
            text = (
                f"[Mock draft {digest}] {prompt[:400]}\n\n"
                f"Key point: be specific and useful. Add one example and one takeaway."
            )
        latency = int((time.time() - t0) * 1000) + 1
        return LLMResult(text, "mock", "mock-1", latency, _tokens(prompt), _tokens(text))


class OpenAICompatibleProvider(BaseProvider):
    """Minimal OpenAI-compatible chat provider via plain HTTP (no SDK dep)."""

    name = "openai_compatible"

    def __init__(self, api_key: str, base_url: str, model: str = "gpt-4o-mini"):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model

    def generate(self, prompt: str, task: str = "generation", max_tokens: int = 800) -> LLMResult:
        t0 = time.time()
        resp = requests.post(
            f"{self.base_url}/chat/completions",
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": max_tokens,
                "temperature": 0.7,
            },
            timeout=60,
        )
        resp.raise_for_status()
        data = resp.json()
        text = data["choices"][0]["message"]["content"]
        usage = data.get("usage", {})
        latency = int((time.time() - t0) * 1000)
        return LLMResult(
            text, "openai_compatible", self.model, latency,
            int(usage.get("prompt_tokens", _tokens(prompt))),
            int(usage.get("completion_tokens", _tokens(text))),
        )
