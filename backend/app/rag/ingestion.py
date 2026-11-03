import pymupdf


def extract_pdf_pages(file_path: str) -> list[dict]:
    """Extract readable text from each page of a PDF."""
    pages = []

    with pymupdf.open(file_path) as document:
        if document.is_encrypted:
            raise ValueError("Encrypted PDFs are not supported.")

        for page_number, page in enumerate(document, start=1):
            text = page.get_text("text").strip()

            if text:
                pages.append({
                    "page": page_number,
                    "text": text,
                })

    return pages


def chunk_pages(
    pages: list[dict],
    chunk_size: int = 1000,
    overlap: int = 150,
) -> list[dict]:
    """Split PDF pages into overlapping text chunks."""
    if chunk_size <= 0 or overlap < 0 or overlap >= chunk_size:
        raise ValueError("Invalid chunk configuration.")

    chunks = []

    for page in pages:
        text = page["text"]
        start = 0

        while start < len(text):
            end = min(start + chunk_size, len(text))

            chunks.append({
                "page": page["page"],
                "text": text[start:end],
            })

            if end == len(text):
                break

            start = end - overlap

    return chunks