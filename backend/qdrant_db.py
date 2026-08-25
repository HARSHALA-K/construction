import logging
from typing import List, Dict, Any
from qdrant_client import QdrantClient, models
from qdrant_client.models import Distance, VectorParams, PointStruct
from .config import QDRANT_URL, QDRANT_API_KEY, QDRANT_COLLECTION_NAME, QDRANT_VECTOR_SIZE, TOP_K
from .utils import get_timestamp
import uuid

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
            _qdrant_client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY, timeout=300)
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
            
            client.create_payload_index(
                collection_name=collection_name,
                field_name="text",
                field_schema=models.TextIndexParams(
                    type="text",
                    tokenizer=models.TokenizerType.WORD,
                    min_token_len=2,
                    max_token_len=15,
                    lowercase=True,
                )
            )
            logger.info(f"Collection '{collection_name}' created.")
        else:
            logger.info(f"Collection '{collection_name}' already exists.")
    except Exception as e:
        logger.error(f"Error creating collection: {e}")
        raise e

def upsert_documents(
        chunks,
        vectors,
        source_document="unknown",
        category="general"
):
    client = connect_qdrant()

    points = []

    timestamp = get_timestamp()

    for idx, (chunk, vector) in enumerate(zip(chunks, vectors)):

        payload = {
            "chunk_id": idx,
            "source_document": source_document,
            "category": category,
            "timestamp": timestamp,
            "text": chunk
        }

        points.append(
            PointStruct(
                id=str(uuid.uuid4()),
                vector=vector,
                payload=payload
            )
        )

    BATCH_SIZE = 5

    try:
        for i in range(0, len(points), BATCH_SIZE):

            batch = points[i:i+BATCH_SIZE]
            print("USING BATCH UPLOAD CODE")
            print(f"Batch size = {len(batch)}")

            client.upsert(
                collection_name=QDRANT_COLLECTION_NAME,
                points=batch
            )

            logger.info(
                f"Uploaded batch "
                f"{i//BATCH_SIZE + 1}/"
                f"{(len(points)-1)//BATCH_SIZE + 1}"
            )

    except Exception as e:
        logger.error(f"Error upserting documents: {e}")
        raise e

def search(query_vector: List[float], query_string: str = None, limit: int = TOP_K) -> List[Dict[str, Any]]:
    """
    Searches the database using vector and optional keyword search and returns a list of dictionaries with text and metadata.
    """
    client = connect_qdrant()
    try:
        results = client.query_points(
            collection_name=QDRANT_COLLECTION_NAME,
            query=query_vector,
            limit=limit
        )
        
        hybrid_results = [point.payload for point in results.points]
        
        if query_string:
            try:
                words = [w for w in query_string.split() if len(w) > 2]
                if words:
                    keyword_results = client.scroll(
                        collection_name=QDRANT_COLLECTION_NAME,
                        scroll_filter=models.Filter(
                            should=[
                                models.FieldCondition(
                                    key="text",
                                    match=models.MatchText(text=word)
                                ) for word in words
                            ]
                        ),
                        limit=limit,
                        with_payload=True
                    )[0]
                else:
                    keyword_results = []
                
                seen_texts = {p.get("text") for p in hybrid_results if p and p.get("text")}
                
                for point in keyword_results:
                    if point.payload and point.payload.get("text") not in seen_texts:
                        hybrid_results.append(point.payload)
                        seen_texts.add(point.payload.get("text"))
            except Exception as e:
                logger.warning(f"Keyword search failed: {e}")
                
        return hybrid_results
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
