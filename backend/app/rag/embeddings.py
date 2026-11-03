from functools import lru_cache

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer


MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


@lru_cache(maxsize=1)
def get_embedding_model():
    """
    Load the embedding model once and reuse it.
    """
    return SentenceTransformer(MODEL_NAME)


def create_embeddings(texts: list[str]) -> np.ndarray:
    """
    Convert text into normalized numerical embeddings.
    """
    if not texts:
        raise ValueError("Cannot create embeddings from an empty list.")

    model = get_embedding_model()

    embeddings = model.encode(
        texts,
        convert_to_numpy=True,
        normalize_embeddings=True,
    )

    return np.asarray(embeddings, dtype=np.float32)


def create_vector_index(embeddings: np.ndarray):
    """
    Build a FAISS index using cosine similarity
    through normalized vectors and inner product.
    """
    if embeddings.ndim != 2 or embeddings.shape[0] == 0:
        raise ValueError("Embeddings must be a non-empty 2D array.")

    dimension = embeddings.shape[1]

    index = faiss.IndexFlatIP(dimension)

    index.add(
        np.ascontiguousarray(embeddings, dtype=np.float32)
    )

    return index


def search_vector_index(
    index,
    query: str,
    top_k: int = 3,
):
    """
    Search for the most similar vectors.
    Returns similarity scores and matching indices.
    """
    if not query.strip():
        raise ValueError("Search query cannot be empty.")

    if top_k < 1:
        raise ValueError("top_k must be at least 1.")

    query_embedding = create_embeddings([query])

    scores, indices = index.search(
        query_embedding,
        min(top_k, index.ntotal),
    )

    return scores[0], indices[0]