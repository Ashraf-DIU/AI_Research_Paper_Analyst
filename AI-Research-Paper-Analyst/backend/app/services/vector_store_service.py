"""One FAISS index per workspace (cosine similarity via normalised vectors + inner product).

The index is persisted to durable storage whenever documents change. It is never rebuilt per query.
If the persisted index is missing it is rebuilt from the chunks saved in the database.
"""
import re
import threading

import faiss
import numpy as np
from rank_bm25 import BM25Okapi
from sqlalchemy.orm import Session

from app.models.paper import Chunk
from app.services.embedding_service import embedder
from app.services.storage_service import storage

_TOKEN_RE = re.compile(r"[A-Za-z0-9_\-\.]+")


def tokenize(text: str) -> list[str]:
    return [t.lower() for t in _TOKEN_RE.findall(text)]


class VectorStore:
    def __init__(self) -> None:
        self._indexes: dict[str, faiss.Index] = {}
        self._bm25: dict[str, tuple[BM25Okapi, list[int]]] = {}
        self._lock = threading.RLock()

    @staticmethod
    def _key(ws: str) -> str:
        return f"indexes/{ws}/index.faiss"

    def _persist(self, ws: str) -> None:
        index = self._indexes.get(ws)
        if index is None:
            return
        storage.put(self._key(ws), faiss.serialize_index(index).tobytes())

    def _new_index(self, dim: int) -> faiss.Index:
        return faiss.IndexIDMap2(faiss.IndexFlatIP(dim))

    def add(self, ws: str, chunk_ids: list[int], vectors: np.ndarray, db: Session | None = None) -> None:
        with self._lock:
            index = self._load(ws, db, rebuild=False)
            if index is None:
                if db is not None and db.query(Chunk.id).filter(
                    Chunk.workspace_id == ws, Chunk.id.notin_(chunk_ids)
                ).first():
                    # Index file was lost (e.g. ephemeral disk) but other papers exist: rebuild everything.
                    self.rebuild(ws, db)
                    return
                index = self._new_index(vectors.shape[1])
                self._indexes[ws] = index
            index.add_with_ids(vectors.astype("float32"), np.array(chunk_ids, dtype="int64"))
            self._bm25.pop(ws, None)
            self._persist(ws)

    def remove(self, ws: str, chunk_ids: list[int], db: Session | None = None) -> None:
        if not chunk_ids:
            return
        with self._lock:
            index = self._load(ws, db, rebuild=False)
            if index is None:
                return
            index.remove_ids(np.array(chunk_ids, dtype="int64"))
            self._bm25.pop(ws, None)
            self._persist(ws)

    def _load(self, ws: str, db: Session | None, rebuild: bool = True):
        if ws in self._indexes:
            return self._indexes[ws]
        key = self._key(ws)
        if storage.exists(key):
            raw = np.frombuffer(storage.get(key), dtype="uint8")
            self._indexes[ws] = faiss.deserialize_index(raw)
            return self._indexes[ws]
        if rebuild and db is not None:
            return self.rebuild(ws, db)
        return None

    def rebuild(self, ws: str, db: Session):
        """Re-embed all chunks of a workspace from the database and persist a fresh index."""
        with self._lock:
            rows = db.query(Chunk.id, Chunk.text).filter(Chunk.workspace_id == ws).order_by(Chunk.id).all()
            self._indexes.pop(ws, None)
            self._bm25.pop(ws, None)
            if not rows:
                return None
            vectors = embedder.embed_documents([r.text for r in rows])
            index = self._new_index(vectors.shape[1])
            index.add_with_ids(vectors, np.array([r.id for r in rows], dtype="int64"))
            self._indexes[ws] = index
            self._persist(ws)
            return index

    def dense_search(self, ws: str, db: Session, query_vec: np.ndarray, k: int) -> list[tuple[int, float]]:
        with self._lock:
            index = self._load(ws, db)
            if index is None or index.ntotal == 0:
                return []
            k = min(k, index.ntotal)
            scores, ids = index.search(query_vec.astype("float32"), k)
        return [(int(i), float(s)) for i, s in zip(ids[0], scores[0]) if i != -1]

    def bm25_search(self, ws: str, db: Session, query: str, k: int) -> list[tuple[int, float]]:
        with self._lock:
            if ws not in self._bm25:
                rows = db.query(Chunk.id, Chunk.text).filter(Chunk.workspace_id == ws).order_by(Chunk.id).all()
                if not rows:
                    return []
                self._bm25[ws] = (BM25Okapi([tokenize(r.text) for r in rows]), [r.id for r in rows])
            bm25, ids = self._bm25[ws]
        scores = bm25.get_scores(tokenize(query))
        order = np.argsort(scores)[::-1][:k]
        return [(ids[i], float(scores[i])) for i in order if scores[i] > 0]


vector_store = VectorStore()
