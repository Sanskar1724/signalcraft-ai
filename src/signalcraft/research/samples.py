"""Offline sample source. Clearly labeled source='sample' — never presented as live news."""
from __future__ import annotations

from .base import ResearchItem

SAMPLES = [
    ResearchItem(
        source="sample", title="AI agents move from demos to data pipelines",
        summary="Teams report using tool-calling agents to scaffold ETL, with human review gates.",
        source_url="sample://agents-data-pipelines", published_at="2026-09-01 10:00:00",
        niche_tags=["AI agents", "Data engineering"],
    ),
    ResearchItem(
        source="sample", title="Small open models close gap on RAG benchmarks",
        summary="Open-weight 7-8B models show strong retrieval-grounded QA with good chunking.",
        source_url="sample://open-models-rag", published_at="2026-09-02 10:00:00",
        niche_tags=["LLMs", "Open source"],
    ),
    ResearchItem(
        source="sample", title="PySpark + LLM: practical patterns for messy data",
        summary="Notes on batching, caching embeddings, and validating LLM-extracted fields.",
        source_url="sample://pyspark-llm", published_at="2026-09-03 10:00:00",
        niche_tags=["PySpark", "Data engineering", "LLMs"],
    ),
]


class SampleSource:
    name = "sample"

    def fetch(self, query: str = "", limit: int = 20) -> list[ResearchItem]:
        if not query:
            return SAMPLES[:limit]
        q = query.lower()
        return [s for s in SAMPLES if q in (s.title + s.summary).lower()][:limit]
