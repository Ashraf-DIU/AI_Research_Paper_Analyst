from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.config import settings
from app.utils.text_utils import build_document, pages_for_range, section_spans


def chunk_pages(pages: list[dict]) -> list[dict]:
    """Section-aware chunking. Every chunk keeps its page range and section name."""
    text, offsets, marks = build_document(pages)
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_chars,
        chunk_overlap=settings.chunk_overlap_chars,
        separators=["\n\n", "\n", ". ", " ", ""],
        add_start_index=True,
    )
    chunks: list[dict] = []
    for start, end, section in section_spans(len(text), marks):
        if section == "References":
            continue  # reference lists pollute retrieval
        segment = text[start:end]
        if not segment.strip():
            continue
        cursor = 0
        for doc in splitter.create_documents([segment]):
            body = doc.page_content.strip()
            if len(body) < 40:
                continue
            idx = doc.metadata.get("start_index", -1)
            idx = cursor if idx < 0 else idx
            cursor = idx
            p0, p1 = pages_for_range(offsets, start + idx, start + idx + len(doc.page_content))
            chunks.append({"text": body, "page_start": p0, "page_end": p1, "section": section})
    for i, c in enumerate(chunks):
        c["chunk_index"] = i
    return chunks
