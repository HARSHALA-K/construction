import logging
from typing import List, Dict, Any
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from .config import QDRANT_URL, QDRANT_API_KEY, QDRANT_COLLECTION_NAME, QDRANT_VECTOR_SIZE, TOP_K
from .utils import get_timestamp

logger = logging.getLogger(__name__)

# Global client for singleton-like behavior
_qdrant_client = None

def connect_qdrant() -> QdrantClient:
    """
    Initializes and returns the Qdrant client (singleton).
    """
    global _qdrant_client
    if _qdrant_client is None:
        try:
            logger.info(f"Connecting to Qdrant at {QDRANT_URL}...")
            _qdrant_client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
            logger.info("Connected to Qdrant successfully.")
        except Exception as e:
            logger.error(f"Failed to connect to Qdrant: {e}")
            raise e
    return _qdrant_client

def create_collection(collection_name: str = QDRANT_COLLECTION_NAME, vector_size: int = QDRANT_VECTOR_SIZE):
    """
    Creates a Qdrant collection if it doesn't already exist.
    """
    client = connect_qdrant()
    try:
        collections_response = client.get_collections()
        collection_names = [col.name for col in collections_response.collections]
        
        if collection_name not in collection_names:
            logger.info(f"Creating collection '{collection_name}'...")
            client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=vector_size,
                    distance=Distance.COSINE
                )
            )
            logger.info(f"Collection '{collection_name}' created.")
        else:
            logger.info(f"Collection '{collection_name}' already exists.")
    except Exception as e:
        logger.error(f"Error creating collection: {e}")
        raise e

def upsert_documents(chunks: List[str], vectors: List[List[float]], source_document: str = "unknown"):
    """
    Upserts text chunks and their vectors into Qdrant with detailed metadata.
    """
    client = connect_qdrant()
    points = []
    
    timestamp = get_timestamp()
    
    for idx, (chunk, vector) in enumerate(zip(chunks, vectors)):
        # Provide the requested metadata
        payload = {
            "chunk_id": str(idx),
            "source_document": source_document,
            "interview_id": "N/A",  # Could be parameterized if needed
            "timestamp": timestamp,
            "text": chunk
        }
        
        points.append(
            PointStruct(
                id=idx,
                vector=vector,
                payload=payload
            )
        )
        
    try:
        logger.info(f"Upserting {len(points)} points into '{QDRANT_COLLECTION_NAME}'...")
        client.upsert(
            collection_name=QDRANT_COLLECTION_NAME,
            points=points
        )
        logger.info("Upsert complete.")
    except Exception as e:
        logger.error(f"Error upserting documents: {e}")
        raise e

def search(query_vector: List[float], limit: int = TOP_K) -> List[Dict[str, Any]]:
    """
    Searches the database and returns a list of dictionaries with text and metadata.
    """
    client = connect_qdrant()
    try:
        results = client.query_points(
            collection_name=QDRANT_COLLECTION_NAME,
            query=query_vector,
            limit=limit
        )
        
        # Return both the text and the metadata to be processed by RAG
        return [point.payload for point in results.points]
    except Exception as e:
        logger.error(f"Error searching Qdrant: {e}")
        raise e

def delete_collection(collection_name: str = QDRANT_COLLECTION_NAME):
    """
    Deletes the specified collection from Qdrant.
    """
    client = connect_qdrant()
    try:
        logger.info(f"Deleting collection '{collection_name}'...")
        client.delete_collection(collection_name=collection_name)
        logger.info(f"Collection '{collection_name}' deleted.")
    except Exception as e:
        logger.error(f"Error deleting collection: {e}")
        raise e
