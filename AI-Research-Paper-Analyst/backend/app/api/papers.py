import uuid
from typing import List

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models.paper import Chunk, Paper
from app.models.workspace import Workspace
from app.schemas.paper import PaperOut
from app.services.ingestion_service import delete_paper_data, process_paper
from app.services.storage_service import storage
from app.utils.pdf_utils import is_pdf, safe_filename, sha256_bytes

router = APIRouter(prefix="/api")


@router.post("/papers/upload", response_model=List[PaperOut])
async def upload_papers(background: BackgroundTasks, workspace_id: str = Form(...),
                        files: List[UploadFile] = File(...), db: Session = Depends(get_db)):
    if not db.get(Workspace, workspace_id):
        raise HTTPException(404, "Workspace not found")
    out = []
    for f in files:
        data = await f.read()
        name = safe_filename(f.filename or "paper.pdf")
        if not name.lower().endswith(".pdf") or not is_pdf(data):
            raise HTTPException(400, f"{name}: only valid PDF files are accepted")
        if len(data) > settings.max_upload_mb * 1024 * 1024:
            raise HTTPException(413, f"{name}: larger than {settings.max_upload_mb} MB")
        digest = sha256_bytes(data)
        existing = db.query(Paper).filter(Paper.workspace_id == workspace_id, Paper.file_hash == digest).first()
        if existing:
            item = PaperOut.model_validate(existing)
            item.duplicate = True
            out.append(item)
            continue
        pid = str(uuid.uuid4())
        key = f"papers/{workspace_id}/{pid}.pdf"
        storage.put(key, data)
        paper = Paper(id=pid, workspace_id=workspace_id, filename=name, file_hash=digest,
                      storage_key=key, status="processing")
        db.add(paper)
        db.commit()
        background.add_task(process_paper, pid)
        out.append(PaperOut.model_validate(paper))
    return out


@router.get("/papers", response_model=List[PaperOut])
def list_papers(workspace_id: str, db: Session = Depends(get_db)):
    return db.query(Paper).filter(Paper.workspace_id == workspace_id).order_by(Paper.created_at.desc()).all()


def _get(db: Session, paper_id: str) -> Paper:
    p = db.get(Paper, paper_id)
    if not p:
        raise HTTPException(404, "Paper not found")
    return p


@router.get("/papers/{paper_id}")
def paper_details(paper_id: str, db: Session = Depends(get_db)):
    from app.models.paper import PaperAnalysis

    p = _get(db, paper_id)
    row = db.get(PaperAnalysis, paper_id)
    out = PaperOut.model_validate(p).model_dump()
    out["chunk_count"] = db.query(Chunk).filter(Chunk.paper_id == paper_id).count()
    out["analysis"] = row.analysis_json if row else None
    return out


@router.get("/papers/{paper_id}/file")
def paper_file(paper_id: str, db: Session = Depends(get_db)):
    p = _get(db, paper_id)
    return Response(storage.get(p.storage_key), media_type="application/pdf",
                    headers={"Content-Disposition": f'inline; filename="{p.filename}"'})


@router.delete("/papers/{paper_id}")
def delete_paper(paper_id: str, db: Session = Depends(get_db)):
    delete_paper_data(db, _get(db, paper_id))
    return {"deleted": paper_id}


@router.get("/tasks/{paper_id}")
def task_status(paper_id: str, db: Session = Depends(get_db)):
    p = _get(db, paper_id)
    return {"id": p.id, "status": p.status, "error_message": p.error_message}
