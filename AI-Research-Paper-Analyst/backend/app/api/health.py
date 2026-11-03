from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.workspace import Workspace
from app.schemas.paper import WorkspaceCreate, WorkspaceOut

router = APIRouter()


@router.get("/api/health")
def health_check():
    return {"status": "healthy", "service": "research-paper-analyst"}


@router.get("/api/workspaces", response_model=list[WorkspaceOut])
def list_workspaces(db: Session = Depends(get_db)):
    return db.query(Workspace).order_by(Workspace.created_at).all()


@router.post("/api/workspaces", response_model=WorkspaceOut)
def create_workspace(body: WorkspaceCreate, db: Session = Depends(get_db)):
    if not body.name.strip():
        raise HTTPException(400, "Name required")
    ws = Workspace(name=body.name.strip()[:200])
    db.add(ws)
    db.commit()
    return ws
