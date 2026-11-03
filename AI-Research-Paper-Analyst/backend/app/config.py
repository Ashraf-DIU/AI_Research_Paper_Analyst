from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "development"
    database_url: str = "sqlite:///./data/app.db"

    # CORS
    frontend_url: str = "http://localhost:3000"
    extra_cors_origins: str = ""      # comma separated
    cors_origin_regex: str = ""       # e.g. https://.*\.vercel\.app for preview deployments

    # LLM (any OpenAI-compatible endpoint: OpenAI, Gemini, Groq, OpenRouter, ...)
    llm_api_key: str = ""
    llm_model: str = "gpt-4o-mini"
    llm_base_url: str = ""
    llm_timeout: int = 90

    # Embeddings
    embedding_provider: str = "local"           # local | api
    embedding_model: str = "BAAI/bge-small-en-v1.5"
    embedding_api_model: str = "text-embedding-3-small"
    embedding_api_key: str = ""                 # falls back to llm_api_key
    embedding_base_url: str = ""                # falls back to llm_base_url
    warmup_embeddings: bool = True

    # Retrieval
    top_k: int = 8
    use_hybrid: bool = True
    use_reranker: bool = False
    reranker_model: str = "BAAI/bge-reranker-base"

    # Chunking (700 tokens ~ 2800 chars, 100 tokens ~ 400 chars)
    chunk_chars: int = 2800
    chunk_overlap_chars: int = 400

    max_upload_mb: int = 25

    # Storage for PDFs and FAISS indexes
    storage_backend: str = "local"              # local | s3
    storage_dir: str = "./data/storage"
    s3_bucket: str = ""
    s3_endpoint_url: str = ""
    s3_region: str = "auto"
    s3_access_key_id: str = ""
    s3_secret_access_key: str = ""

    @property
    def sqlalchemy_url(self) -> str:
        url = self.database_url
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql+psycopg://", 1)
        elif url.startswith("postgresql://"):
            url = url.replace("postgresql://", "postgresql+psycopg://", 1)
        return url

    @property
    def cors_origins(self) -> list[str]:
        origins = ["http://localhost:3000", self.frontend_url.rstrip("/")]
        origins += [o.strip().rstrip("/") for o in self.extra_cors_origins.split(",") if o.strip()]
        return sorted(set(origins))


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
