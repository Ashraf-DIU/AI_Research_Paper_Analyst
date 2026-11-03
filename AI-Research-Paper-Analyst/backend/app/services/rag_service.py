from sqlalchemy.orm import Session

from app.models.conversation import Conversation, Message
from app.prompts import QA_SYSTEM
from app.services.llm_service import complete
from app.services.retrieval_service import retrieve
from app.utils.citation_utils import build_context, validate_citations

ABSTAIN = "The provided papers do not contain enough evidence to answer this."


def answer_question(db: Session, workspace_id: str, question: str,
                    paper_ids: list[str] | None = None, conversation_id: str | None = None) -> dict:
    convo = db.get(Conversation, conversation_id) if conversation_id else None
    if convo is None or convo.workspace_id != workspace_id:
        convo = Conversation(workspace_id=workspace_id)
        db.add(convo)
        db.flush()

    history = (db.query(Message).filter(Message.conversation_id == convo.id)
               .order_by(Message.id.desc()).limit(6).all())[::-1]
    db.add(Message(conversation_id=convo.id, role="user", content=question))

    chunks = retrieve(db, workspace_id, question, paper_ids=paper_ids)
    if not chunks:
        answer, citations, grounded, warning = ABSTAIN + " No relevant passages were found.", [], False, None
    else:
        context, sources = build_context(chunks)
        hist = "\n".join(f"{m.role}: {m.content[:500]}" for m in history)
        user = (f"Conversation so far:\n{hist}\n\n" if hist else "") + \
               f"Sources:\n{context}\n\nQuestion: {question}"
        raw = complete(QA_SYSTEM, user)
        answer, citations = validate_citations(raw, sources)
        grounded = bool(citations)
        abstained = "do not contain enough evidence" in answer.lower()
        warning = None if (grounded or abstained) else \
            "The answer contains no valid citations to the retrieved sources; treat it as unverified."

    db.add(Message(conversation_id=convo.id, role="assistant", content=answer, citations=citations))
    db.commit()
    return {"conversation_id": convo.id, "answer": answer, "citations": citations,
            "grounded": grounded, "warning": warning}
