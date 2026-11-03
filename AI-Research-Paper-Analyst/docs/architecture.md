# Architecture
Upload -> validate (%PDF, size, SHA-256 dedupe) -> store PDF -> background job: PyMuPDF per-page text -> header/footer cleaning ->
section detection -> section-aware chunking (page range per chunk) -> BGE embeddings -> FAISS (IndexIDMap2, per workspace, persisted to storage).
Query: dense + BM25 -> Reciprocal Rank Fusion -> optional cross-encoder rerank -> numbered context [S#] -> LLM -> citation validation
(invalid tags removed; ungrounded answers flagged). The FAISS index is updated on upload/delete, never per query, and rebuilt from DB chunks if lost.
