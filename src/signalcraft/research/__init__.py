"""Research subpackage (§8: RSS, GitHub, Reddit, YouTube, News, web search, trends)."""
from .base import BaseSource, ResearchItem
from .extra_sources import (
                            GitHubSource,
                            NewsSource,
                            RedditSource,
                            SearchTrendsSource,
                            WebSearchSource,
                            YouTubeSource,
)
from .manager import collect_and_store, list_recent, search
from .normalize import (
                            BANNED_URL_TOKENS,
                            clean_text,
                            looks_like_url_junk,
                            normalize_doc,
                            strip_html,
)
from .rss import RSSSource
from .samples import SampleSource

__all__ = [
                            "BANNED_URL_TOKENS",
                            "BaseSource",
                            "GitHubSource",
                            "NewsSource",
                            "RSSSource",
                            "RedditSource",
                            "ResearchItem",
                            "SampleSource",
                            "SearchTrendsSource",
                            "WebSearchSource",
                            "YouTubeSource",
                            "clean_text",
                            "collect_and_store",
                            "list_recent",
                            "looks_like_url_junk",
                            "normalize_doc",
                            "search",
                            "strip_html",
]
