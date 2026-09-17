import uuid
import enum
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime
from sqlalchemy.orm import relationship
from backend.app.database import Base


class UserRole(str, enum.Enum):
    admin = "admin"
    recruiter = "recruiter"
    student = "student"

VALID_ROLES = [r.value for r in UserRole]

class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), default="recruiter", nullable=False)
    location = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    jds = relationship("JobDescription", back_populates="creator")
    uploaded_resumes = relationship(
        "Resume", back_populates="uploader", foreign_keys="Resume.uploaded_by"
    )
