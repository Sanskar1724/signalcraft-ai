"""LLM provider registry (§21). App code uses get_gateway(), never providers directly."""
from __future__ import annotations

from signalcraft.config import settings
from signalcraft.llm import LLMGateway
from signalcraft.llm.providers import (
    MockProvider,
    OpenAICompatibleProvider,
    OpenRouterProvider,
)

__all__ = ["PROVIDERS", "get_gateway"]

PROVIDERS = ("mock", "openrouter", "openai_compatible")


def get_gateway(name: str = "default") -> LLMGateway:
    if name == "mock":
        return LLMGateway(provider=MockProvider())
    if name == "openrouter":
        return LLMGateway(provider=OpenRouterProvider(
            settings.openrouter_api_key or "unset", settings.openrouter_base_url))
    if name == "openai_compatible":
        return LLMGateway(provider=OpenAICompatibleProvider(
            settings.openai_api_key or "unset", settings.openai_base_url))
    return LLMGateway()  # env-based default
