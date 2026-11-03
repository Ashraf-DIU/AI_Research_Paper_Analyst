"""Rebuild FAISS index(es) from chunks stored in the database.  Usage: python scripts/rebuild_index.py [workspace_id]"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))
from app.database import SessionLocal  # noqa: E402
from app.models.workspace import Workspace  # noqa: E402
from app.services.vector_store_service import vector_store  # noqa: E402

db = SessionLocal()
ids = [sys.argv[1]] if len(sys.argv) > 1 else [w.id for w in db.query(Workspace).all()]
for ws in ids:
    idx = vector_store.rebuild(ws, db)
    print(ws, "->", idx.ntotal if idx else 0, "vectors")
