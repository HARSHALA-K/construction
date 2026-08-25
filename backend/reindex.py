import os

from backend.utils import read_txt, chunk_text
from backend.pdf_loader import read_pdf
from backend.embedding import embed_documents
from backend.qdrant_db import (
    delete_collection,
    create_collection,
    upsert_documents
)

# --------------------------------
# Recreate collection
# --------------------------------

delete_collection()
create_collection()

# --------------------------------
# Existing QA file
# --------------------------------

qa_text = read_txt("data/construction_qa.txt")

qa_chunks = chunk_text(qa_text)

qa_vectors = embed_documents(qa_chunks)

upsert_documents(
    qa_chunks,
    qa_vectors,
    source_document="construction_qa.txt",
    category="qa"
)

# --------------------------------
# Materials PDF
# --------------------------------

materials_text = read_pdf("data/materials.pdf")

materials_chunks = chunk_text(materials_text)

materials_vectors = embed_documents(materials_chunks)

upsert_documents(
    materials_chunks,
    materials_vectors,
    source_document="materials.pdf",
    category="materials"
)

# --------------------------------
# Safety PDF
# --------------------------------

safety_text = read_pdf("data/safety.pdf")

safety_chunks = chunk_text(safety_text)

safety_vectors = embed_documents(safety_chunks)

upsert_documents(
    safety_chunks,
    safety_vectors,
    source_document="safety.pdf",
    category="safety"
)
