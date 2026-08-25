import logging
from typing import List
from .config import EMBEDDING_MODEL_NAME

logger = logging.getLogger(__name__)

# Global model variable for singleton-like behavior
_embedding_model = None

def load_embedding_model():
    """
    Loads the sentence-transformers model. Called once during initialization.
    """
    global _embedding_model
    if _embedding_model is None:
        logger.info(f"Loading embedding model '{EMBEDDING_MODEL_NAME}'...")
        from sentence_transformers import SentenceTransformer
        _embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)
        logger.info("Embedding model loaded successfully.")

def _get_model():
    if _embedding_model is None:
        load_embedding_model()
    return _embedding_model

def embed_text(text: str) -> List[float]:
    """
    Generates an embedding for a single text string.
    """
    model = _get_model()
    return model.encode(text).tolist()

def embed_documents(documents: List[str]) -> List[List[float]]:
    """
    Generates embeddings for a list of text documents.
    """
    model = _get_model()
    return model.encode(documents).tolist()
