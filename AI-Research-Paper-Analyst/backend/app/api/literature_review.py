from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import load_papers
from app.schemas.chat import ReviewRequest
from app.services.literature_review_service import generate_review

router = APIRouter(prefix="/api")


@router.post("/literature-review")
def literature_review(body: ReviewRequest, db: Session = Depends(get_db)):
    papers = load_papers(db, body.workspace_id, body.paper_ids)
    return generate_review(db, body.workspace_id, body.topic, papers, body.sections,
                           body.citation_style, body.word_count)
