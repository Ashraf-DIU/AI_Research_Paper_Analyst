import fitz  # PyMuPDF


def extract_pdf_pages(data: bytes) -> tuple[list[dict], dict]:
    """Extract text page by page, preserving the original 1-based page numbers."""
    doc = fitz.open(stream=data, filetype="pdf")
    try:
        pages = [{"page_number": i + 1, "text": page.get_text("text")} for i, page in enumerate(doc)]
        meta = doc.metadata or {}
    finally:
        doc.close()
    return pages, meta
