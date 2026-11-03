
import threading
import uuid

from app.db.database import SessionLocal
from app.db.models import Document
from app.rag.embeddings import (
    create_embeddings,
    create_vector_index,
    search_vector_index,
)
from app.rag.ingestion import (
    extract_pdf_pages,
    chunk_pages,
)
from app.services.document_storage import get_pdf_path


# In-memory FAISS cache.
# Missing indexes are rebuilt from persisted PDFs.
DOCUMENTS = {}
LOCK = threading.RLock()


def index_document(
    filename: str,
    jurisdiction: str,
    chunks: list[dict],
    document_id: str | None = None,
) -> str:
    """
    Generate embeddings and cache a document
    under a stable document ID.
    """

    if jurisdiction not in ("US", "IN"):
        raise ValueError("Unsupported jurisdiction.")

    if not chunks:
        raise ValueError("Cannot index an empty document.")

    texts = [chunk["text"] for chunk in chunks]

    embeddings = create_embeddings(texts)
    vector_index = create_vector_index(embeddings)

    if document_id is None:
        document_id = str(uuid.uuid4())

    with LOCK:
        DOCUMENTS[document_id] = {
            "filename": filename,
            "jurisdiction": jurisdiction,
            "chunks": chunks,
            "index": vector_index,
        }

    return document_id


def restore_document(document_id: str) -> bool:
    """
    Restore a missing FAISS index from a PDF
    recorded in PostgreSQL.
    """

    with LOCK:
        if document_id in DOCUMENTS:
            return True

    db = SessionLocal()

    try:
        document = db.get(Document, document_id)

        if document is None:
            return False

        pdf_path = get_pdf_path(document.storage_id)

        pages = extract_pdf_pages(str(pdf_path))

        if not pages:
            raise ValueError(
                "Stored PDF contains no extractable text."
            )

        chunks = chunk_pages(pages)

        if not chunks:
            raise ValueError(
                "Stored PDF contains no usable chunks."
            )

        index_document(
            filename=document.filename,
            jurisdiction=document.jurisdiction,
            chunks=chunks,
            document_id=document.id,
        )

        return True

    finally:
        db.close()


def search_document(
    document_id: str,
    question: str,
    jurisdiction: str,
    top_k: int = 4,
) -> list[dict]:
    """
    Search relevant passages, restoring the
    FAISS index when necessary.
    """

    if not question.strip():
        raise ValueError("Question cannot be empty.")

    if top_k < 1:
        raise ValueError("top_k must be at least 1.")

    with LOCK:
        document = DOCUMENTS.get(document_id)

    if document is None:
        restored = restore_document(document_id)

        if not restored:
            raise KeyError(
                "Document not found in PostgreSQL."
            )

        with LOCK:
            document = DOCUMENTS.get(document_id)

    if document is None:
        raise KeyError("Unable to restore document.")

    if document["jurisdiction"] != jurisdiction:
        raise ValueError(
            "Document jurisdiction does not match "
            "the selected jurisdiction."
        )

    scores, indices = search_vector_index(
        index=document["index"],
        query=question,
        top_k=top_k,
    )

    results = []

    for score, index in zip(scores, indices):
        if index < 0:
            continue

        chunk = document["chunks"][int(index)]

        results.append({
            "document_id": document_id,
            "filename": document["filename"],
            "page": chunk["page"],
            "text": chunk["text"],
            "score": float(score),
        })

    return results


def delete_document(document_id: str) -> bool:
    """
    Remove a document from the FAISS cache.
    This does not delete the stored PDF or DB record.
    """

    with LOCK:
        return DOCUMENTS.pop(document_id, None) is not None
