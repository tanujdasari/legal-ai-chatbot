from app.rag.ingestion import (
    extract_pdf_pages,
    chunk_pages,
)

from app.rag.retriever import (
    index_document,
    search_document,
    delete_document,
)


def main():
    print("STEP 1: Extracting PDF text...")

    pages = extract_pdf_pages("sample_contract.pdf")

    assert pages, "No text extracted from the PDF."

    print("Pages extracted:", len(pages))

    print("\nSTEP 2: Chunking document...")

    chunks = chunk_pages(pages)

    assert chunks, "No chunks generated."

    print("Chunks created:", len(chunks))

    print("\nSTEP 3: Indexing document...")

    document_id = index_document(
        filename="sample_contract.pdf",
        jurisdiction="US",
        chunks=chunks,
    )

    print("Document ID:", document_id)

    print("\nSTEP 4: Searching document...")

    question = "When is the rent due?"

    results = search_document(
        document_id=document_id,
        question=question,
        jurisdiction="US",
        top_k=3,
    )

    assert results, "No search results returned."

    print("Question:", question)

    for rank, result in enumerate(results, start=1):
        print(f"\nResult {rank}")
        print("Filename:", result["filename"])
        print("Page:", result["page"])
        print("Similarity:", round(result["score"], 4))
        print("Text:", result["text"])

    assert any(
        "first day of each month" in result["text"]
        for result in results
    ), "Expected rental payment passage was not retrieved."

    print("\nSTEP 5: Testing jurisdiction isolation...")

    try:
        search_document(
            document_id=document_id,
            question=question,
            jurisdiction="IN",
        )
    except ValueError:
        print("Jurisdiction isolation passed.")
    else:
        raise AssertionError(
            "Jurisdiction mismatch was not rejected."
        )

    print("\nSTEP 6: Deleting test document...")

    assert delete_document(document_id) is True

    try:
        search_document(
            document_id=document_id,
            question=question,
            jurisdiction="US",
        )
    except KeyError:
        print("Document deletion passed.")
    else:
        raise AssertionError(
            "Deleted document is still searchable."
        )

    print("\nALL RETRIEVER TESTS PASSED")


if __name__ == "__main__":
    main()