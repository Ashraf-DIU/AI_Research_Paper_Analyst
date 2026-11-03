from typing import List

from pydantic import BaseModel, Field


class CompareRequest(BaseModel):
    workspace_id: str
    paper_ids: List[str] = Field(min_length=2, max_length=6)
    summarize: bool = True
