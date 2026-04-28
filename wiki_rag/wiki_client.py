"""Small MediaWiki client for assignment ingestion."""

from __future__ import annotations

import json
import urllib.parse
import urllib.request
from dataclasses import dataclass


WIKI_API_URL = "https://en.wikipedia.org/w/api.php"

WIKI_TITLE_OVERRIDES = {
    "Christ the Redeemer": "Christ the Redeemer (statue)",
}


@dataclass(frozen=True)
class WikiDocument:
    title: str
    source_url: str
    content: str


class WikipediaError(RuntimeError):
    pass


def wikipedia_url(title: str) -> str:
    return "https://en.wikipedia.org/wiki/" + urllib.parse.quote(title.replace(" ", "_"))


def fetch_wikipedia_page(title: str, timeout: int = 30) -> WikiDocument:
    fetch_title = WIKI_TITLE_OVERRIDES.get(title, title)
    params = {
        "action": "query",
        "format": "json",
        "redirects": "1",
        "prop": "extracts",
        "explaintext": "1",
        "titles": fetch_title,
    }
    url = WIKI_API_URL + "?" + urllib.parse.urlencode(params)
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "local-wikipedia-rag-assistant/1.0 "
            "(educational local RAG project)"
        },
    )

    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except OSError as exc:
        raise WikipediaError(f"Could not fetch Wikipedia page for {title}: {exc}") from exc

    pages = payload.get("query", {}).get("pages", {})
    if not pages:
        raise WikipediaError(f"Wikipedia returned no pages for {title}")

    page = next(iter(pages.values()))
    if "missing" in page:
        raise WikipediaError(f"Wikipedia page not found: {title}")

    normalized_title = page.get("title", title)
    content = (page.get("extract") or "").strip()
    if not content:
        raise WikipediaError(f"Wikipedia page had no extract text: {title}")

    return WikiDocument(
        title=normalized_title,
        source_url=wikipedia_url(normalized_title),
        content=content,
    )
