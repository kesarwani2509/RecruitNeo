from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from backend.app.database import get_db
from backend.app.core.deps import get_current_user, require_role
from backend.app.models.user import User
from backend.app.models.job_description import JobDescription
from backend.app.models.evaluation import Evaluation
from backend.app.schemas.jd import JDCreate, JDResponse, JDListItem
from backend.app.parser.jd_parser import parse_jd

router = APIRouter(prefix="/api/jds", tags=["job-descriptions"])


@router.post("", response_model=JDResponse)
def create_jd(
    payload: JDCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("recruiter", "admin")),
):
    structured = parse_jd(
        payload.raw_text,
        title=payload.title,
        company=payload.company,
        location=payload.location,
    )
    jd = JobDescription(
        title=payload.title,
        company=payload.company,
        location=payload.location or structured.get("location"),
        min_experience=payload.min_experience if payload.min_experience is not None else structured.get("min_experience"),
        max_experience=payload.max_experience if payload.max_experience is not None else structured.get("max_experience"),
        raw_text=payload.raw_text,
        structured_fields=structured,
        created_by=current_user.id,
    )
    db.add(jd)
    db.commit()
    db.refresh(jd)
    return jd


@router.get("", response_model=List[JDListItem])
def list_jds(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    jds = db.query(JobDescription).order_by(JobDescription.created_at.desc()).all()
    result = []
    for jd in jds:
        count = db.query(Evaluation).filter(Evaluation.jd_id == jd.id).count()
        item = JDListItem.model_validate(jd)
        item.candidate_count = count
        result.append(item)
    return result


@router.get("/{jd_id}", response_model=JDResponse)
def get_jd(jd_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    jd = db.query(JobDescription).filter(JobDescription.id == jd_id).first()
    if not jd:
        raise HTTPException(status_code=404, detail="JD not found")
    return jd


@router.delete("/{jd_id}")
def delete_jd(
    jd_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("recruiter", "admin")),
):
    jd = db.query(JobDescription).filter(JobDescription.id == jd_id).first()
    if not jd:
        raise HTTPException(status_code=404, detail="JD not found")
    if current_user.role == "recruiter" and jd.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="You can only delete job openings you created")
    db.delete(jd)
    db.commit()
    return {"status": "deleted"}