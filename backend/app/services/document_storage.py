
from pathlib import Path
from uuid import UUID, uuid4

STORAGE_DIR = (
    Path(__file__).resolve().parents[2]
    / "storage"
    / "documents"
)

MAX_PDF_SIZE = 10 * 1024 * 1024


def save_pdf(file_bytes: bytes) -> tuple[str, Path]:
    """Save PDF bytes under a unique storage ID."""

    if not file_bytes:
        raise ValueError("PDF file is empty.")

    if len(file_bytes) > MAX_PDF_SIZE:
        raise ValueError("PDF exceeds 10 MB limit.")

    if not file_bytes.startswith(b"%PDF-"):
        raise ValueError("Invalid PDF file signature.")

    STORAGE_DIR.mkdir(parents=True, exist_ok=True)

    storage_id = str(uuid4())
    file_path = STORAGE_DIR / f"{storage_id}.pdf"

    with file_path.open("xb") as file:
        file.write(file_bytes)

    return storage_id, file_path


def get_pdf_path(storage_id: str) -> Path:
    """Find a stored PDF using its UUID."""

    safe_id = str(UUID(storage_id))
    file_path = STORAGE_DIR / f"{safe_id}.pdf"

    if not file_path.is_file():
        raise FileNotFoundError("PDF not found.")

    return file_path


def delete_pdf(storage_id: str) -> bool:
    """Delete a stored PDF."""

    try:
        file_path = get_pdf_path(storage_id)
    except FileNotFoundError:
        return False

    file_path.unlink()
    return True
