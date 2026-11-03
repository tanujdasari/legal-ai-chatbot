
import os
import tempfile
from pathlib import Path

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
)
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import Document
from app.rag.ingestion import extract_pdf_pages, chunk_pages
from app.rag.retriever import index_document, delete_document
from app.services.document_storage import save_pdf, delete_pdf

router = APIRouter(
    prefix="/api/documents",
    tags=["Legal Documents"],
)

MAX_FILE_SIZE = 10 * 1024 * 1024


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    jurisdiction: str = Form(...),
    db: Session = Depends(get_db),
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
    storage_id = None
    document_id = None

    filename = Path(file.filename.replace("\\", "/")).name

    try:
        # Read the uploaded PDF in bounded chunks.
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
            file_bytes = saved_file.read()

        if not file_bytes.startswith(b"%PDF-"):
            raise HTTPException(
                status_code=400,
                detail="Invalid PDF file.",
            )

        # Extract text before persisting the document.
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

        if not chunks:
            raise HTTPException(
                status_code=422,
                detail="No usable text chunks found.",
            )

        # Store the original PDF on disk.
        storage_id, saved_path = save_pdf(file_bytes)

        # Create the FAISS index for immediate use.
        document_id = index_document(
            filename=filename,
            jurisdiction=jurisdiction,
            chunks=chunks,
        )

        # Save metadata in PostgreSQL.
        document = Document(
            id=document_id,
            filename=filename,
            jurisdiction=jurisdiction,
            storage_id=storage_id,
        )

        db.add(document)
        db.commit()

        return {
            "document_id": document_id,
            "filename": filename,
            "jurisdiction": jurisdiction,
            "pages": len(pages),
            "chunks": len(chunks),
            "status": "indexed",
        }

    except HTTPException:
        db.rollback()
        if document_id:
            delete_document(document_id)
        if storage_id:
            delete_pdf(storage_id)
        raise

    except Exception as exc:
        db.rollback()

        if document_id:
            delete_document(document_id)

        if storage_id:
            delete_pdf(storage_id)

        raise HTTPException(
            status_code=422,
            detail="Unable to process the PDF.",
        ) from exc

    finally:
        await file.close()

        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)
