import logging
from typing import Dict, Any, Tuple, List
from .embedding import embed_text
from .qdrant_db import search as qdrant_search
from .llm import generate_answer
from .router import route_query
import re

logger = logging.getLogger(__name__)


def answer_question(
    query: str,
    backend: str = "qdrant",
    history: List[Dict] = None,
    web_results: List[Dict[str, Any]] = None
) -> Tuple[str, List[Dict[str, Any]]]:

    logger.info(f"Processing query: {query}")

    try:

        context_chunks = []
        source_metadata = []

        # -----------------------------------------------------
        # 1. WEB SEARCH (Highest Priority)
        # -----------------------------------------------------


        if web_results:
            web_text = []

            for item in web_results:
                title = item.get("title", "")
                text = item.get("text", "")
                url = item.get("url", "")

                web_text.append(
                    f"Title: {title}\n"
                    f"Summary: {text}\n"
                    f"URL: {url}"
                )

                # Add web result to source metadata
                source_metadata.append({
                    "chunk_id": None,
                    "source_document": title,
                    "category": "web",
                    "timestamp": None,
                    "text": text,
                    "url": url
                })

            context_chunks.append(
                "LATEST WEB INFORMATION:\n\n"
                + "\n\n".join(web_text)
            )

        # -----------------------------------------------------
        # 2. VECTOR SEARCH (RAG)
        # -----------------------------------------------------

        if backend == "qdrant":

            search_queries = []
            
            # Simple heuristic or LLM check: If the paragraph contains multiple requests

            def split_search_queries(query: str) -> List[str]:
                """
                Split a multi-part user query into independent search queries.
                Keeps the original query when no reliable split is found.
                """

                # Split on common conjunctions
                parts = re.split(
                    r"\s+(?:and|also|additionally|plus)\s+|[,;]",
                    query,
                    flags=re.IGNORECASE
                )

                # Clean empty pieces
                parts = [part.strip() for part in parts if part.strip()]

                # Avoid creating bad searches from very small fragments
                if len(parts) <= 1:
                    return [query.strip()]

                valid_parts = [
                    part for part in parts
                    if len(part.split()) >= 3
                ]

                return valid_parts if valid_parts else [query.strip()]
            search_queries = split_search_queries(query)

            logger.info(
                f"Generated search queries: {search_queries}"
            )

            # Loop through all extracted queries to gather complete context
            for sub_query in search_queries:
                logger.info(f"Searching Qdrant for sub-query: {sub_query}")
                query_vector = embed_text(sub_query)
                results = qdrant_search(query_vector, query_string=sub_query)
                
                for item in results:
                    text_content = item.get("text", "")
                    if text_content not in context_chunks:
                        context_chunks.append(text_content)
                        source_metadata.append(item)

        elif backend == "aws":

            raise NotImplementedError(
                "AWS backend not implemented."
            )

        else:

            raise ValueError(
                f"Unknown backend {backend}"
            )

        # -----------------------------------------------------
        # 3. BUILD CONTEXT
        # -----------------------------------------------------

        context = "\n\n".join(context_chunks)

        # -----------------------------------------------------
        # 4. BUILD HISTORY
        # -----------------------------------------------------

        history_text = ""

        if history:

            history_text = "\n".join(
                f"{msg['role']}: {msg['content']}"
                for msg in history[-5:]
            )

        # -----------------------------------------------------
        # 5. GENERATE FINAL ANSWER
        # -----------------------------------------------------

        answer = generate_answer(
            question=query,
            context=context,
            history=history_text
        )
        
        logger.info("Successfully generated answer.")
        return answer, source_metadata
        
    except Exception as e:
        logger.error(f"Error in RAG pipeline: {e}")
        raise e
