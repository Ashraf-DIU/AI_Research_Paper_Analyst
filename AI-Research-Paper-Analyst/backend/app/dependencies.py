from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.paper import Paper
from app.models.workspace import Workspace


def get_workspace(workspace_id: str, db: Session = Depends(get_db)) -> Workspace:
    ws = db.get(Workspace, workspace_id)
    if not ws:
        raise HTTPException(404, "Workspace not found")
    return ws


def load_papers(db: Session, workspace_id: str, paper_ids: list[str] | None, require_ready: bool = True) -> list[Paper]:
    """Always scoped to the workspace so one workspace can never read another's papers."""
    q = db.query(Paper).filter(Paper.workspace_id == workspace_id)
    if require_ready:
        q = q.filter(Paper.status == "ready")
    if paper_ids:
        q = q.filter(Paper.id.in_(paper_ids))
    papers = q.order_by(Paper.created_at).all()
    if paper_ids and len(papers) != len(set(paper_ids)):
        raise HTTPException(400, "Some papers were not found in this workspace or are not ready yet.")
    if not papers:
        raise HTTPException(400, "No ready papers found.")
    return papers
