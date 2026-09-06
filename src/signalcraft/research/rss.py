"""RSS research source. Stdlib XML, no extra dependency. Preserves source URLs."""
from __future__ import annotations

import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from itertools import islice

import requests

from ..observability import log
from .base import ResearchItem

DEFAULT_FEEDS = [
    "https://hnrss.org/newest?q=AI+agents",
    "https://hnrss.org/newest?q=LLM",
    "https://hnrss.org/newest?q=data+engineering",
]


class RSSSource:
    name = "rss"

    def __init__(self, feeds: list[str] | None = None, timeout: int = 15):
        self.feeds = feeds or DEFAULT_FEEDS
        self.timeout = timeout

    def fetch(self, query: str = "", limit: int = 20) -> list[ResearchItem]:
        items: list[ResearchItem] = []
        for feed in self.feeds:
            try:
                r = requests.get(feed, timeout=self.timeout,
                                 headers={"User-Agent": "SignalCraftAI/0.1"})
                r.raise_for_status()
                root = ET.fromstring(r.content)
                for it in islice(root.iter("item"), limit):
                    title = (it.findtext("title") or "").strip()
                    link = (it.findtext("link") or "").strip()
                    desc = (it.findtext("description") or "").strip()[:600]
                    pub = (it.findtext("pubDate") or "").strip()
                    if not title:
                        continue
                    if query and query.lower() not in (title + desc).lower():
                        continue
                    items.append(ResearchItem(
                        source="rss", title=title, summary=desc,
                        source_url=link, published_at=pub or _now(),
                    ))
            except Exception as e:
                log.warning("RSS feed failed %s: %s", feed, e)
                continue
        return items[:limit]


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
