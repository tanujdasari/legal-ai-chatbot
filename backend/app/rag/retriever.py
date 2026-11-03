import threading
import uuid

from app.rag.embeddings import (
    create_embeddings,
    create_vector_index,
    search_vector_index,
)


# Development-only, in-memory document storage.
# Documents are lost when the backend restarts.
DOCUMENTS = {}
LOCK = threading.RLock()


def index_document(
    filename: str,
    jurisdiction: str,
    chunks: list[dict],
) -> str:
    """
    Convert document chunks into embeddings,
    create a FAISS index, and store the document.
    """

    if jurisdiction not in ("US", "IN"):
        raise ValueError("Unsupported jurisdiction.")

    if not chunks:
        raise ValueError("Cannot index an empty document.")

    texts = [chunk["text"] for chunk in chunks]

    embeddings = create_embeddings(texts)
    vector_index = create_vector_index(embeddings)

    document_id = str(uuid.uuid4())

    with LOCK:
        DOCUMENTS[document_id] = {
            "filename": filename,
            "jurisdiction": jurisdiction,
            "chunks": chunks,
            "index": vector_index,
        }

    return document_id


def search_document(
    document_id: str,
    question: str,
    jurisdiction: str,
    top_k: int = 4,
) -> list[dict]:
    """
    Find document passages most relevant
    to the user's question.
    """

    if not question.strip():
        raise ValueError("Question cannot be empty.")

    if top_k < 1:
        raise ValueError("top_k must be at least 1.")

    with LOCK:
        document = DOCUMENTS.get(document_id)

    if document is None:
        raise KeyError("Document not found. Upload it again.")

    if document["jurisdiction"] != jurisdiction:
        raise ValueError(
            "Document jurisdiction does not match the selected jurisdiction."
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
    Remove a document from the in-memory store.
    """

    with LOCK:
        return DOCUMENTS.pop(document_id, None) is not None