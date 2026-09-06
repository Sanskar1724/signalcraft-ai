"""Pluggable source stubs (§8). Each implements fetch() so new sources need no core rewrite.
MVP returns [] offline; wire real APIs later without touching manager.py.
Covers: GitHub, Reddit, YouTube, News, Web search, Search trends (§8)."""
from __future__ import annotations

from .base import ResearchItem


class GitHubSource:
    name = "github"

    def __init__(self, token: str = ""):
        self.token = token

    def fetch(self, query: str = "", limit: int = 20) -> list[ResearchItem]:
        # TODO: call api.github.com/search/repositories. Offline MVP: empty.
        return []


class RedditSource:
    name = "reddit"

    def fetch(self, query: str = "", limit: int = 20) -> list[ResearchItem]:
        # TODO: subreddit search via public JSON. Offline MVP: empty.
        return []


class YouTubeSource:
    name = "youtube"

    def __init__(self, api_key: str = ""):
        self.api_key = api_key

    def fetch(self, query: str = "", limit: int = 20) -> list[ResearchItem]:
        # TODO: YouTube Data API search. Offline MVP: empty.
        return []


class NewsSource:
    name = "news"

    def __init__(self, api_key: str = ""):
        self.api_key = api_key

    def fetch(self, query: str = "", limit: int = 20) -> list[ResearchItem]:
        # TODO: NewsAPI/GDELT query. Offline MVP: empty.
        return []


class WebSearchSource:
    name = "websearch"

    def __init__(self, api_key: str = ""):
        self.api_key = api_key

    def fetch(self, query: str = "", limit: int = 20) -> list[ResearchItem]:
        # TODO: web search provider. Offline MVP: empty.
        return []


class SearchTrendsSource:
    name = "search_trends"

    def fetch(self, query: str = "", limit: int = 20) -> list[ResearchItem]:
        # TODO: Google Trends / industry sources. Offline MVP: empty.
        return []
