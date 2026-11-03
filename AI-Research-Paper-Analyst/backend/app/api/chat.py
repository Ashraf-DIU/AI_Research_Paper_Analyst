from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import load_papers
from app.models.conversation import Conversation, Message
from app.models.workspace import Workspace
from app.schemas.chat import ChatRequest
from app.services.rag_service import answer_question

router = APIRouter(prefix="/api")


@router.post("/chat")
def chat(body: ChatRequest, db: Session = Depends(get_db)):
    if not db.get(Workspace, body.workspace_id):
        raise HTTPException(404, "Workspace not found")
    if body.paper_ids:
        load_papers(db, body.workspace_id, body.paper_ids)
    return answer_question(db, body.workspace_id, body.question, body.paper_ids, body.conversation_id)


@router.get("/chat/{conversation_id}")
def get_conversation(conversation_id: str, db: Session = Depends(get_db)):
    c = db.get(Conversation, conversation_id)
    if not c:
        raise HTTPException(404, "Conversation not found")
    msgs = db.query(Message).filter(Message.conversation_id == c.id).order_by(Message.id).all()
    return {"id": c.id, "workspace_id": c.workspace_id,
            "messages": [{"role": m.role, "content": m.content, "citations": m.citations or []} for m in msgs]}
