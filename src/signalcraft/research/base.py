"""Research source interface."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass
class ResearchItem:
    source: str
    title: str
    summary: str = ""
    source_url: str = ""
    published_at: str = ""
    niche_tags: list[str] | None = None


class BaseSource(Protocol):
    name: str

    def fetch(self, query: str = "", limit: int = 20) -> list[ResearchItem]:
        ...
