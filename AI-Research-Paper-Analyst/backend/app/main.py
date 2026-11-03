import threading
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import analysis, chat, comparison, health, literature_review, papers, research_gaps
from app.config import settings
from app.database import SessionLocal, init_db
from app.models.workspace import Workspace
from app.services.embedding_service import embedder
from app.services.llm_service import LLMNotConfigured


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    db = SessionLocal()
    try:
        if not db.query(Workspace).first():
            db.add(Workspace(name="Default workspace"))
            db.commit()
    finally:
        db.close()
    if settings.warmup_embeddings:
        threading.Thread(target=embedder.warmup, daemon=True).start()
    yield


app = FastAPI(title="AI Research Paper Analyst", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_origin_regex=settings.cors_origin_regex or None,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

for r in (health, papers, analysis, chat, comparison, research_gaps, literature_review):
    app.include_router(r.router)


@app.exception_handler(LLMNotConfigured)
async def llm_not_configured(_: Request, exc: LLMNotConfigured):
    return JSONResponse(status_code=503, content={"detail": str(exc)})


@app.get("/")
def root():
    return {"message": "Research Paper Analyst API", "docs": "/docs"}
