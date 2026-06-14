"""ADK tool: live web search via Tavily.

Complements the static paper corpus with current / post-publication information
("latest", "2026", recent releases) the papers can't contain. Like rag_search, it
appends its results to session state `retrieved_context` so the Reviewer checks
web-sourced claims against the actual snippets too.
"""
import os

from google.adk.tools import ToolContext
from tavily import TavilyClient

from src.config import RETRIEVED_CONTEXT

MAX_RESULTS = 5
_client: TavilyClient | None = None


def _get_client() -> TavilyClient:
    """Lazily build one Tavily client (key read at call time, after .env loads)."""
    global _client
    if _client is None:
        _client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])
    return _client


def web_search(query: str, tool_context: ToolContext) -> dict:
    """Search the live web for current or recent information.

    Use this for the latest developments, recent releases, news, or anything that
    post-dates the corpus papers (signals: "latest", "recent", "2025", "2026",
    "newest", "today", or named systems/events that came after the literature).

    Args:
        query: A focused natural-language search query.

    Returns:
        A dict with `source` = "web", `answer` (Tavily's short synthesis), and
        `results`, a list of {title, url, content} snippets.
    """
    resp = _get_client().search(
        query,
        search_depth="advanced",
        max_results=MAX_RESULTS,
        include_answer=True,
    )
    results = [
        {"title": r.get("title"), "url": r.get("url"), "content": r.get("content")}
        for r in resp.get("results", [])
    ]
    evidence = list(tool_context.state.get(RETRIEVED_CONTEXT, []))
    evidence.extend(
        {"origin": "web", "citation": r["url"], "text": r["content"]} for r in results
    )
    tool_context.state[RETRIEVED_CONTEXT] = evidence
    return {"source": "web", "answer": resp.get("answer"), "results": results}
