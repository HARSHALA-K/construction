import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ==========================================
# API Keys & Secrets
# ==========================================
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

# ==========================================
# Model Configurations
# ==========================================
WHISPER_MODEL_NAME = "medium"
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
LLM_MODEL = "llama-3.3-70b-versatile"

# ==========================================
# Retrieval Configurations
# ==========================================
TOP_K = 17
TEMPERATURE = 0.2
QDRANT_COLLECTION_NAME = "construction_qa"
QDRANT_VECTOR_SIZE = 384

# ==========================================
# Prompt Templates
# ==========================================
RAG_PROMPT_TEMPLATE = """
You are a construction domain assistant.

Answer the question using only the provided context.

If the answer is not present in the context, say:
"I do not have enough information."

Context:
{context}

Question:
{question}

Answer:
"""
