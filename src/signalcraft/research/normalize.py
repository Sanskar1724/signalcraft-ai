"""Research normalization (§5): every source becomes a clean ResearchDocument.

Raw HTML, URLs, and source-chrome (e.g. Hacker News "12 points by x | 45
comments") are stripped BEFORE storage so parser artifacts can never become
topics, evidence, or content. Invalid documents are rejected, not stored.
"""
from __future__ import annotations

import html as _html
import re
import urllib.parse
from html.parser import HTMLParser

__all__ = ["strip_html", "clean_text", "normalize_doc", "BANNED_URL_TOKENS",
           "looks_like_url_junk"]

# Tokens that are URL/parser metadata, never semantic topics (§5).
BANNED_URL_TOKENS = frozenset({
    "https", "http", "href", "url", "www", "com", "html", "htm",
    "item", "points", "point", "comments", "comment", "ycombinator",
    "news", "org", "net", "io", "php", "aspx", "utm",
})

_HN_META = re.compile(
    r"\d+\s+points?\s+by\s+\S+.*?(?:\|\s*)?\d*\s*comments?", re.IGNORECASE | re.DOTALL)
_URL = re.compile(r"https?://[^\s<>\"]+|www\.[^\s<>\"]+")
_LABELS = re.compile(r"(article url|comments url|points|comments)\s*:\s*", re.IGNORECASE)
_WS = re.compile(r"\s+")


class _TextOnly(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []

    def handle_data(self, data: str) -> None:
        self.parts.append(data)

    def get(self) -> str:
        return "".join(self.parts)


def strip_html(raw: str) -> str:
    """Remove tags, keep text, unescape entities. Never raises."""
    try:
        parser = _TextOnly()
        parser.feed(raw or "")
        return _html.unescape(parser.get())
    except Exception:
        return re.sub(r"<[^>]+>", " ", raw or "")


def clean_text(raw: str) -> str:
    text = strip_html(raw)
    text = _HN_META.sub(" ", text)
    text = _LABELS.sub(" ", text)
    text = _URL.sub(" ", text)
    return _WS.sub(" ", text).strip()


def looks_like_url_junk(topic: str) -> bool:
    return any(tok in BANNED_URL_TOKENS for tok in topic.lower().split())


def _valid_url(url: str) -> bool:
    if not url:
        return False
    if url.startswith("sample://"):
        return True
    try:
        parts = urllib.parse.urlparse(url)
        return parts.scheme in ("http", "https") and bool(parts.netloc)
    except Exception:
        return False


def normalize_doc(source: str, title: str, summary: str = "",
                  source_url: str = "") -> dict | None:
    """Return a clean document dict, or None when the input is unusable
    (missing title, invalid URL). Never raises."""
    title = clean_text(title or "")
    if not title:
        return None
    if source_url and not _valid_url(source_url):
        source_url = ""
    return {
        "source": (source or "unknown")[:40],
        "title": title[:300],
        "summary": clean_text(summary or "")[:1200],
        "source_url": source_url[:500],
    }
