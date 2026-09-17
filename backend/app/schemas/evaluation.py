from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from uuid import UUID

class EvaluationResponse(BaseModel):
    id: UUID
    resume_id: UUID
    jd_id: UUID
    relevance_score: int
    keyword_score: Optional[float] = None
    semantic_score: Optional[float] = None
    experience_score: Optional[float] = None
    certification_score: Optional[float] = None
    fit_verdict: str
    missing_skills: Optional[List[str]] = None
    missing_certs: Optional[List[str]] = None
    missing_projects: Optional[List[str]] = None
    feedback_text: Optional[str] = None
    evaluated_at: datetime
    jd_title: Optional[str] = None
    model_config = {"from_attributes": True}

class ScoreBreakdown(BaseModel):
    keyword_score: float
    semantic_score: float
    experience_score: float
    certification_score: float
    relevance_score: int
    fit_verdict: str

class EvaluationDetail(EvaluationResponse):
    candidate_name: Optional[str] = None
    candidate_email: Optional[str] = None
    jd_title: str
    jd_location: Optional[str] = None
    resume_location: Optional[str] = None
    score_breakdown: dict
