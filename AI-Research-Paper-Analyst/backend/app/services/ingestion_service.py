"""Background processing of an uploaded PDF: extract -> clean -> chunk -> embed -> index."""
from app.database import SessionLocal
from app.models.paper import Chunk, Paper
from app.services.chunking_service import chunk_pages
from app.services.embedding_service import embedder
from app.services.pdf_service import extract_pdf_pages
from app.services.storage_service import storage
from app.services.vector_store_service import vector_store
from app.utils.text_utils import clean_pages, find_doi, guess_title


def process_paper(paper_id: str) -> None:
    db = SessionLocal()
    paper = db.get(Paper, paper_id)
    if paper is None:
        db.close()
        return
    try:
        pages, meta = extract_pdf_pages(storage.get(paper.storage_key))
        total_chars = sum(len(p["text"].strip()) for p in pages)
        if total_chars < 200 * max(1, min(len(pages), 3)):
            raise ValueError("No extractable text found. This looks like a scanned PDF (OCR is not enabled).")
        pages = clean_pages(pages)
        chunks = chunk_pages(pages)
        if not chunks:
            raise ValueError("No usable text chunks were produced from this PDF.")

        paper.title = guess_title(pages, meta.get("title"))
        paper.doi = find_doi(pages)
        paper.num_pages = len(pages)

        rows = [
            Chunk(paper_id=paper.id, workspace_id=paper.workspace_id, chunk_index=c["chunk_index"],
                  text=c["text"], page_start=c["page_start"], page_end=c["page_end"], section=c["section"])
            for c in chunks
        ]
        db.add_all(rows)
        db.flush()  # assigns chunk ids

        vectors = embedder.embed_documents([r.text for r in rows])
        vector_store.add(paper.workspace_id, [r.id for r in rows], vectors, db)
        paper.status, paper.error_message = "ready", None
        db.commit()
    except Exception as exc:
        db.rollback()
        paper = db.get(Paper, paper_id)
        if paper:
            paper.status, paper.error_message = "failed", str(exc)[:1000]
            db.commit()
    finally:
        db.close()


def delete_paper_data(db, paper: Paper) -> None:
    ids = [r.id for r in db.query(Chunk.id).filter(Chunk.paper_id == paper.id).all()]
    vector_store.remove(paper.workspace_id, ids, db)
    db.query(Chunk).filter(Chunk.paper_id == paper.id).delete()
    from app.models.paper import PaperAnalysis

    db.query(PaperAnalysis).filter(PaperAnalysis.paper_id == paper.id).delete()
    storage.delete(paper.storage_key)
    db.delete(paper)
    db.commit()
