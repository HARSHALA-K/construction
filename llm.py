import logging
from groq import Groq
from .config import GROQ_API_KEY, LLM_MODEL, RAG_PROMPT_TEMPLATE, TEMPERATURE

logger = logging.getLogger(__name__)

# Global client for singleton-like behavior
_llm_client = None

def initialize_llm() -> Groq:
    """
    Initializes and returns the Groq client.
    """
    global _llm_client
    if _llm_client is None:
        try:
            logger.info("Initializing Groq client...")
            _llm_client = Groq(api_key=GROQ_API_KEY)
            logger.info("Groq client initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize Groq client: {e}")
            raise e
    return _llm_client

def generate_answer(query: str, context: str) -> str:
    """
    Constructs the prompt with the given context and query, and generates an answer using Groq.
    """
    client = initialize_llm()
    
    prompt = RAG_PROMPT_TEMPLATE.format(context=context, question=query)
    
    try:
        logger.info(f"Generating answer for query using {LLM_MODEL}...")
        response = client.chat.completions.create(
            model=LLM_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=TEMPERATURE
        )
        logger.info("Answer generated successfully.")
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Error generating answer from LLM: {e}")
        raise e
