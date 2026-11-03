import threading

import numpy as np

from app.config import settings

BGE_QUERY_PREFIX = "Represent this sentence for searching relevant passages: "


class Embedder:
    """BGE locally (sentence-transformers) or any OpenAI-compatible embeddings API."""

    def __init__(self) -> None:
        self._model = None
        self._client = None
        self._lock = threading.Lock()

    def _load_local(self):
        with self._lock:
            if self._model is None:
                from sentence_transformers import SentenceTransformer

                self._model = SentenceTransformer(settings.embedding_model)
        return self._model

    def _api(self):
        if self._client is None:
            from openai import OpenAI

            key = settings.embedding_api_key or settings.llm_api_key
            if not key:
                raise RuntimeError("EMBEDDING_PROVIDER=api requires EMBEDDING_API_KEY or LLM_API_KEY.")
            self._client = OpenAI(
                api_key=key, base_url=(settings.embedding_base_url or settings.llm_base_url or None)
            )
        return self._client

    @staticmethod
    def _normalize(v: np.ndarray) -> np.ndarray:
        v = np.asarray(v, dtype="float32")
        norms = np.linalg.norm(v, axis=1, keepdims=True)
        return v / np.clip(norms, 1e-12, None)

    def _embed(self, texts: list[str]) -> np.ndarray:
        if settings.embedding_provider == "api":
            out = []
            client = self._api()
            for i in range(0, len(texts), 64):
                resp = client.embeddings.create(model=settings.embedding_api_model, input=texts[i : i + 64])
                out.extend(d.embedding for d in resp.data)
            return self._normalize(np.array(out))
        model = self._load_local()
        return self._normalize(model.encode(texts, batch_size=32, normalize_embeddings=True))

    def embed_documents(self, texts: list[str]) -> np.ndarray:
        return self._embed(texts)

    def embed_query(self, query: str) -> np.ndarray:
        if settings.embedding_provider != "api" and "bge" in settings.embedding_model.lower():
            query = BGE_QUERY_PREFIX + query
        return self._embed([query])

    def warmup(self) -> None:
        try:
            if settings.embedding_provider != "api":
                self._load_local()
        except Exception as exc:  # warm-up must never crash the server
            print(f"[warmup] embedding model not loaded: {exc}")


embedder = Embedder()
