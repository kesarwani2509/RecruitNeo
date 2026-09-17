from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID

class JDCreate(BaseModel):
    title: str
    company: Optional[str] = None
    location: Optional[str] = None
    min_experience: Optional[int] = None
    max_experience: Optional[int] = None
    raw_text: str

class JDResponse(BaseModel):
    id: UUID
    title: str
    company: Optional[str] = None
    location: Optional[str] = None
    min_experience: Optional[int] = None
    max_experience: Optional[int] = None
    raw_text: str
    structured_fields: dict
    created_by: UUID
    created_at: datetime
    model_config = {"from_attributes": True}

class JDListItem(BaseModel):
    id: UUID
    title: str
    company: Optional[str] = None
    location: Optional[str] = None
    min_experience: Optional[int] = None
    max_experience: Optional[int] = None
    structured_fields: dict = {}
    created_by: Optional[UUID] = None
    created_at: datetime
    candidate_count: int = 0
    model_config = {"from_attributes": True}