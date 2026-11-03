import os
import tempfile

from fastapi import (
    APIRouter,
    File,
    Form,
    HTTPException,
    UploadFile,
)

from app.rag.ingestion import extract_pdf_pages, chunk_pages
from app.rag.retriever import index_document

router = APIRouter(
    prefix="/api/documents",
    tags=["Legal Documents"],
)

MAX_FILE_SIZE = 10 * 1024 * 1024


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    jurisdiction: str = Form(...),
):
    if jurisdiction not in ("US", "IN"):
        raise HTTPException(
            status_code=422,
            detail="Jurisdiction must be US or IN.",
        )

    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported.",
        )

    temp_path = None

    try:
        with tempfile.NamedTemporaryFile(
            suffix=".pdf",
            delete=False,
        ) as temp_file:
            temp_path = temp_file.name
            total_bytes = 0

            while True:
                chunk = await file.read(1024 * 1024)

                if not chunk:
                    break

                total_bytes += len(chunk)

                if total_bytes > MAX_FILE_SIZE:
                    raise HTTPException(
                        status_code=413,
                        detail="PDF must be 10 MB or smaller.",
                    )

                temp_file.write(chunk)

        with open(temp_path, "rb") as saved_file:
            if saved_file.read(5) != b"%PDF-":
                raise HTTPException(
                    status_code=400,
                    detail="Invalid PDF file.",
                )

        pages = extract_pdf_pages(temp_path)

        if not pages:
            raise HTTPException(
                status_code=422,
                detail=(
                    "No extractable text found. "
                    "Scanned PDFs require OCR support."
                ),
            )

        chunks = chunk_pages(pages)

        document_id = index_document(
            filename=os.path.basename(file.filename),
            jurisdiction=jurisdiction,
            chunks=chunks,
        )

        return {
            "document_id": document_id,
            "filename": os.path.basename(file.filename),
            "jurisdiction": jurisdiction,
            "pages": len(pages),
            "chunks": len(chunks),
            "status": "indexed",
        }

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=422,
            detail="Unable to process the PDF.",
        ) from exc

    finally:
        await file.close()

        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)