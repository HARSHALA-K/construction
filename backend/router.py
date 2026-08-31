import time
from ddgs import DDGS

WEB_SEARCH_CACHE = {}
CACHE_EXPIRY_SECONDS = 300


def route_query(user_query: str) -> list:
    """
    DuckDuckGo Web Search with caching.
    Returns structured web results containing title, text and URL.
    """

    optimized_query = (
        f"India construction building civil engineering {user_query}"
    )

    current_time = time.time()

    # ---------------- Cache ----------------
    if optimized_query in WEB_SEARCH_CACHE:
        timestamp, cached = WEB_SEARCH_CACHE[optimized_query]

        if current_time - timestamp < CACHE_EXPIRY_SECONDS:
            return cached

    try:
        with DDGS() as ddgs:
            results = list(
                ddgs.text(
                    optimized_query,
                    max_results=5
                )
            )

        if not results:
            return []

        web_sources = []

        for item in results:
            web_sources.append({
                "title": item.get("title", ""),
                "text": item.get("body", ""),
                "url": item.get("href", "")
            })

        WEB_SEARCH_CACHE[optimized_query] = (
            current_time,
            web_sources
        )

        print("DEBUG WEB SEARCH RESULTS:", web_sources)

        return web_sources

    except Exception as e:
        print("WEB SEARCH ERROR:", e)
        return []