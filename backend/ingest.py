from backend.pdf_loader import read_pdf
from backend.embedding import embed_documents
from backend.qdrant_db import upsert_documents
from backend.utils import chunk_text, read_txt
from backend.qdrant_db import (
    delete_collection,
    create_collection,
    upsert_documents
)
delete_collection()
create_collection()

documents = [
    ("data/construction_qa.txt", "qa", "txt"),
    ("data/materials.pdf", "materials", "pdf"),
    ("data/safety.pdf", "safety", "pdf"),
]

for file_path, category, file_type in documents:

    if file_type == "txt":
        text = read_txt(file_path)

    elif file_type == "pdf":
        text = read_pdf(file_path)

    chunks = chunk_text(text)

    vectors = embed_documents(chunks)
    print(f"Max chunk size: {max(len(c) for c in chunks)}")
    print(f"Average chunk size: {sum(len(c) for c in chunks)/len(chunks):.2f}")

    upsert_documents(
        chunks,
        vectors,
        source_document=file_path.split("/")[-1],
        category=category
    )

    print(f"{file_path}: {len(chunks)} chunks uploaded.")
    print(f"Text length: {len(text)}")
    print(f"Chunks generated: {len(chunks)}")