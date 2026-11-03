from typing import List, Optional

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    question: str = Field(min_length=3, max_length=2000)
    workspace_id: str
    conversation_id: Optional[str] = None
    paper_ids: Optional[List[str]] = None


class GapRequest(BaseModel):
    workspace_id: str
    paper_ids: List[str] = Field(min_length=2)


class ReviewRequest(BaseModel):
    workspace_id: str
    topic: str = Field(min_length=3, max_length=300)
    paper_ids: Optional[List[str]] = None
    sections: Optional[List[str]] = None
    citation_style: str = "numeric"      # numeric | numeric-page
    word_count: int = Field(default=900, ge=300, le=4000)
