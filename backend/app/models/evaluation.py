import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, Float, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from backend.app.database import Base


class Evaluation(Base):
    __tablename__ = "evaluations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    resume_id = Column(String(36), ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False)
    jd_id = Column(String(36), ForeignKey("job_descriptions.id", ondelete="CASCADE"), nullable=False)
    relevance_score = Column(Integer, nullable=False)
    keyword_score = Column(Float, nullable=True)
    semantic_score = Column(Float, nullable=True)
    experience_score = Column(Float, nullable=True)
    certification_score = Column(Float, nullable=True)
    fit_verdict = Column(String(10), nullable=False)
    missing_skills = Column(JSON, default=list)
    missing_certs = Column(JSON, default=list)
    missing_projects = Column(JSON, default=list)
    feedback_text = Column(Text, nullable=True)
    evaluated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    resume = relationship("Resume", back_populates="evaluations")
    jd = relationship("JobDescription", back_populates="evaluations")
