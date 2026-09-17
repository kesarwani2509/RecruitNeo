from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID


class ResumeResponse(BaseModel):
    id: UUID
    filename: str
    candidate_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    entities: dict
    uploaded_by: UUID
    created_at: datetime
    model_config = {"from_attributes": True}
