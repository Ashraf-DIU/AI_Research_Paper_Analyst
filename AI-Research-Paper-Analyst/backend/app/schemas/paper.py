from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class WorkspaceCreate(BaseModel):
    name: str


class WorkspaceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    name: str


class PaperOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    workspace_id: str
    filename: str
    title: Optional[str] = None
    doi: Optional[str] = None
    num_pages: int = 0
    status: str
    error_message: Optional[str] = None
    created_at: datetime
    duplicate: bool = False
