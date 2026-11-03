from typing import List, Optional

from pydantic import BaseModel, Field


class Finding(BaseModel):
    value: str
    evidence: str = ""
    page: Optional[int] = None
    verified: bool = False   # True when the quote was found verbatim in the retrieved text


class ResearchPaperAnalysis(BaseModel):
    title: Optional[Finding] = None
    research_objective: Optional[Finding] = None
    methodology: Optional[Finding] = None
    datasets: List[Finding] = Field(default_factory=list)
    models: List[Finding] = Field(default_factory=list)
    evaluation_metrics: List[Finding] = Field(default_factory=list)
    key_results: List[Finding] = Field(default_factory=list)
    limitations: List[Finding] = Field(default_factory=list)
    future_work: List[Finding] = Field(default_factory=list)
