from signalcraft.llm import LLMGateway
from signalcraft.llm.providers import MockProvider


def test_mock_generate_deterministic():
    g = LLMGateway(provider=MockProvider())
    a = g.generate("hello world", task="strategy")
    b = g.generate("hello world", task="strategy")
    assert a == b
    assert len(a) > 20


def test_embed_norm():
    g = LLMGateway(provider=MockProvider())
    v = g.embed("ai agents data pipelines")
    assert len(v) == 64
    assert abs(sum(x * x for x in v) - 1.0) < 1e-6


def test_structured_generate_returns_dict():
    g = LLMGateway(provider=MockProvider())
    out = g.structured_generate("classify this", task="classification")
    assert isinstance(out, dict)
