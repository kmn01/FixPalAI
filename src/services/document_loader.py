"""Document loading: PDF and text parsing."""

from pathlib import Path
from typing import Iterator

from pydantic import BaseModel


class DocumentChunk(BaseModel):
    """A chunk of document content with metadata."""

    content: str
    source: str
    source_type: str  # "manual", "user"
    domain: str | None = None  # plumbing, electrical, carpentry, hvac
    page: int | None = None
    section: str | None = None


def load_pdf(path: str | Path) -> Iterator[DocumentChunk]:
    """Load a PDF file and yield page-by-page chunks (raw pages; chunking applied separately)."""
    import fitz  # PyMuPDF

    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"PDF not found: {path}")

    doc = fitz.open(path)
    try:
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text = page.get_text()
            if text.strip():
                yield DocumentChunk(
                    content=text,
                    source=str(path.name),
                    source_type="manual",
                    page=page_num + 1,
                )
    finally:
        doc.close()


def load_text(path: str | Path, source_type: str = "transcript") -> Iterator[DocumentChunk]:
    """Load a plain text file."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Text file not found: {path}")

    content = path.read_text(encoding="utf-8", errors="replace")
    if content.strip():
        yield DocumentChunk(
            content=content,
            source=str(path.name),
            source_type=source_type,
        )


def load_document(path: str | Path, source_type: str = "manual") -> Iterator[DocumentChunk]:
    """Load a document (PDF or text) based on extension."""
    path = Path(path)
    suffix = path.suffix.lower()

    if suffix == ".pdf":
        yield from load_pdf(path)
    elif suffix in (".txt", ".text"):
        yield from load_text(path, source_type=source_type)
    else:
        raise ValueError(f"Unsupported file type: {suffix}")
