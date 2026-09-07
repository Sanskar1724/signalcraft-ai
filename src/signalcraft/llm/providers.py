"""LLM provider abstraction (§21). Mock works offline; OpenRouter is the
initial live provider; OpenAI-compatible covers the rest. App code must use
LLMGateway, never a provider directly."""
from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field

import requests


@dataclass
class LLMResult:
    text: str
    provider: str
    model: str
    latency_ms: int
    prompt_tokens: int
    completion_tokens: int
    cost_usd: float = 0.0


class BaseProvider:
    name = "base"

    def generate(self, prompt: str, task: str = "generation", max_tokens: int = 800) -> LLMResult:
        raise NotImplementedError


def _tokens(s: str) -> int:
    return max(1, len(s) // 4)


class MockProvider(BaseProvider):
    """Deterministic offline provider. Never calls network. Good for tests/dev.

    Emits clean, leak-free text (provenance is tracked in llm_requests, not
    in the words). Sanitizers treat this like any other provider output.
    """

    name = "mock"

    def generate(self, prompt: str, task: str = "generation", max_tokens: int = 800) -> LLMResult:
        t0 = time.time()
        # Deterministic per input so tests and demos are reproducible.
        digest = hashlib.md5(f"{task}:{prompt}".encode()).hexdigest()
        seed = int(digest[:8], 16)
        if task == "strategy":
            angles = [
                "Commit to one sharp angle and prove it with a concrete example.",
                "Take the contrarian view and support it with specific evidence.",
                "Turn the insight into a practical before/after story.",
            ]
            text = (angles[seed % len(angles)] + " Structure: a concrete hook, "
                    "three specific insights, one piece of proof, and a direct "
                    "call to action. Avoid generic hype; use examples.")
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
            bodies = [
                "Start with the most surprising specific detail. Make one claim, "
                "support it with a concrete example, and end with a single takeaway "
                "the reader can use this week.",
                "Open on a real scenario the reader recognizes. Explain what changed, "
                "why it matters now, and give one practical next step.",
                "Lead with a clear opinion. Back it with observed evidence, note one "
                "limitation honestly, and close with what to try next.",
            ]
            text = bodies[seed % len(bodies)]
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


class OpenRouterProvider(BaseProvider):
    """Initial live provider (§21): OpenRouter chat completions + cost tracking."""

    name = "openrouter"

    # Approximate $/1K tokens (prompt, completion); refined from API usage when present.
    PRICE_PER_1K = {
        "openai/gpt-4o-mini": (0.00015, 0.0006),
        "openai/gpt-4o": (0.0025, 0.01),
        "anthropic/claude-3-5-sonnet": (0.003, 0.015),
        "google/gemini-flash-1.5": (0.000075, 0.0003),
    }

    def __init__(self, api_key: str, base_url: str, model: str = "openai/gpt-4o-mini"):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model

    def _cost(self, pt: int, ct: int) -> float:
        if self.model == "openrouter/free" or self.model.endswith(":free"):
            return 0.0
        pr, cr = self.PRICE_PER_1K.get(self.model, (0.001, 0.003))
        return round(pt / 1000 * pr + ct / 1000 * cr, 6)

    def generate(self, prompt: str, task: str = "generation", max_tokens: int = 800) -> LLMResult:
        t0 = time.time()
        resp = requests.post(
            f"{self.base_url}/chat/completions",
            headers={"Authorization": f"Bearer {self.api_key}",
                     "HTTP-Referer": "https://signalcraft.ai",
                     "X-Title": "SignalCraft AI"},
            json={"model": self.model,
                  "messages": [{"role": "user", "content": prompt}],
                  "max_tokens": max_tokens, "temperature": 0.7},
            timeout=60,
        )
        resp.raise_for_status()
        data = resp.json()
        try:
            msg = data["choices"][0]["message"]
        except (KeyError, IndexError, TypeError):
            raise ValueError(f"unexpected OpenRouter response: {str(data)[:200]}")
        text = msg.get("content") or ""
        if isinstance(text, list):  # content-block responses
            text = "".join(b.get("text", "") for b in text if isinstance(b, dict))
        if not text:  # reasoning models may put output here
            text = msg.get("reasoning", "") or ""
        if not text:
            raise ValueError("empty model response (content and reasoning both empty)")
        usage = data.get("usage", {})
        pt = int(usage.get("prompt_tokens", _tokens(prompt)))
        ct = int(usage.get("completion_tokens", _tokens(text)))
        return LLMResult(text, "openrouter", self.model,
                         int((time.time() - t0) * 1000), pt, ct, self._cost(pt, ct))
