import time
from ddgs import DDGS

WEB_SEARCH_CACHE = {}
CACHE_EXPIRY_SECONDS = 300


async def route_query(user_query: str) -> str:
    """
    DuckDuckGo Web Search with caching.
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
            return ""

        snippets = []

        for item in results:

            snippets.append(
                f"""
Title:
{item.get('title','')}

Summary:
{item.get('body','')}
"""
            )

        final_text = "\n".join(snippets)

        WEB_SEARCH_CACHE[optimized_query] = (
            current_time,
            final_text
        )

        return final_text

    except Exception as e:

        return ""