"""Research subpackage (§8: RSS, GitHub, Reddit, YouTube, News, web search, trends)."""
from .base import BaseSource, ResearchItem
from .extra_sources import (GitHubSource, NewsSource, RedditSource,
                            SearchTrendsSource, WebSearchSource, YouTubeSource)
from .manager import collect_and_store, list_recent, search
from .rss import RSSSource
from .samples import SampleSource

__all__ = ["BaseSource", "ResearchItem", "RSSSource", "SampleSource",
           "GitHubSource", "RedditSource", "YouTubeSource", "NewsSource",
           "WebSearchSource", "SearchTrendsSource",
           "collect_and_store", "list_recent", "search"]
