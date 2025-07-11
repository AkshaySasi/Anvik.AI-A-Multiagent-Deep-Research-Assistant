from pydantic import BaseModel
from typing import List

class Paper(BaseModel):
    title: str
    authors: List[str]
    year: int
    abstract: str
    doi: str
    url: str

class PaperSummary(BaseModel):
    title: str
    authors: List[str]
    year: int
    abstract: str
    summary: str
    doi: str
    url: str

class ResearchReport(BaseModel):
    topic: str
    wikipedia_summary: str
    paper_summaries: List[PaperSummary]
    citations_apa: List[str]
    citations_mla: List[str]
    generated_at: str