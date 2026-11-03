from app.rag.embeddings import (
    create_embeddings,
    create_vector_index,
    search_vector_index,
)


def main():
    documents = [
        "The tenant must pay rent on the first day of each month.",
        "The employee is entitled to annual paid leave.",
        "The contract may be terminated with 30 days written notice.",
        "A company must comply with applicable tax regulations.",
    ]

    print("Creating document embeddings...")

    embeddings = create_embeddings(documents)

    print("Embedding shape:", embeddings.shape)

    assert embeddings.shape == (4, 384)

    print("Creating FAISS index...")

    index = create_vector_index(embeddings)

    assert index.ntotal == 4

    question = "When does the tenant need to pay rent?"

    print("\nQuestion:", question)

    scores, indices = search_vector_index(
        index,
        question,
        top_k=3,
    )

    print("\nTop matching documents:")

    for rank, (score, idx) in enumerate(
        zip(scores, indices),
        start=1,
    ):
        print(f"\nRank {rank}")
        print(f"Similarity: {score:.4f}")
        print(f"Document: {documents[int(idx)]}")

    assert int(indices[0]) == 0, (
        "Expected the rental payment passage to rank first."
    )

    print("\nTEST PASSED")


if __name__ == "__main__":
    main()