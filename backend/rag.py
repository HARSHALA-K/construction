import logging
from typing import Dict, Any, Tuple, List
from .embedding import embed_text
from .qdrant_db import search as qdrant_search
from .llm import generate_answer
from .router import route_query

logger = logging.getLogger(__name__)


def answer_question(
    query: str,
    backend: str = "qdrant",
    history: List[Dict] = None,
    web_results: str = None
) -> Tuple[str, List[Dict[str, Any]]]:

    logger.info(f"Processing query: {query}")

    try:

        context_chunks = []
        source_metadata = []

        # -----------------------------------------------------
        # 1. WEB SEARCH (Highest Priority)
        # -----------------------------------------------------


        if web_results:
            context_chunks.append(
                "LATEST WEB INFORMATION:\n"
                + web_results
            )

        # -----------------------------------------------------
        # 2. VECTOR SEARCH (RAG)
        # -----------------------------------------------------

        if backend == "qdrant":

            search_queries = []
            
            # Simple heuristic or LLM check: If the paragraph contains multiple requests
            if any(word in query.lower() for word in ["and", ",", "also", "addition"]):
                # Use your routing/LLM logic to split into standalone search strings
                # If route_query doesn't split, fallback to treating the query as a list
                try:
                    # Modify your route_query or a helper to return a list of sub-queries
                    # For now, we fallback to running the main query if splitting fails
                    search_queries = [query] 
                except Exception:
                    search_queries = [query]
            else:
                search_queries = [query]

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
