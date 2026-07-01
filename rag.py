import logging
from typing import Dict, Any, Tuple, List
from .embedding import embed_text
from .qdrant_db import search as qdrant_search
from .llm import generate_answer

logger = logging.getLogger(__name__)

def answer_question(question: str, backend: str = "qdrant") -> Tuple[str, List[Dict[str, Any]]]:
    """
    Takes a query, retrieves relevant context from the specified backend, 
    and generates an answer using the LLM.
    
    Returns:
        Tuple containing (the_answer_string, list_of_source_metadata_dicts)
    """
    logger.info(f"Processing query: '{question}' with backend '{backend}'")
    
    try:
        # Generate embedding for the query
        query_vector = embed_text(question)
        
        # Retrieve relevant context based on backend
        context_chunks = []
        source_metadata = []
        
        if backend == "qdrant":
            results = qdrant_search(query_vector)
            for item in results:
                context_chunks.append(item.get("text", ""))
                source_metadata.append(item)
        elif backend == "aws":
            # Placeholder for future AWS backend (e.g. OpenSearch Serverless)
            logger.warning("AWS backend is not yet implemented.")
            raise NotImplementedError("AWS backend is not yet implemented.")
        else:
            raise ValueError(f"Unknown backend: {backend}")
            
        context_string = "\n\n".join(context_chunks)
        
        if not context_string:
            logger.warning("No retrieved context found for the query.")
            # Still call the LLM, maybe it has some fallback or the prompt handles empty context
            
        # Generate answer using LLM
        answer = generate_answer(question, context_string)
        
        logger.info("Successfully generated answer.")
        return answer, source_metadata
        
    except Exception as e:
        logger.error(f"Error in RAG pipeline: {e}")
        raise e
