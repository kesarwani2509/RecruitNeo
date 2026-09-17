from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from backend.app.database import get_db
from backend.app.core.deps import get_current_user
from backend.app.models.user import User
from backend.app.models.evaluation import Evaluation
from backend.app.models.resume import Resume
from backend.app.schemas.evaluation import EvaluationResponse, EvaluationDetail

router = APIRouter(prefix="/api/evaluations", tags=["evaluations"])


@router.get("", response_model=List[EvaluationResponse])
def list_evaluations(
    jd_id: Optional[str] = Query(None),
    verdict: Optional[str] = Query(None),
    min_score: Optional[int] = Query(None),
    location: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Evaluation)
    if current_user.role == "student":
        query = query.join(Evaluation.resume).filter(Resume.uploaded_by == current_user.id)
    if jd_id:
        query = query.filter(Evaluation.jd_id == jd_id)
    if verdict:
        query = query.filter(Evaluation.fit_verdict == verdict)
    if min_score is not None:
        query = query.filter(Evaluation.relevance_score >= min_score)
    results = query.order_by(Evaluation.relevance_score.desc()).all()

    if location:
        filtered = []
        for e in results:
            resume = e.resume
            if (resume.entities or {}).get("location", "").lower() == location.lower():
                filtered.append(e)
        results = filtered

    out = []
    for e in results:
        item = EvaluationResponse.model_validate(e)
        item.jd_title = e.jd.title if e.jd else None
        out.append(item)
    return out


@router.get("/{evaluation_id}", response_model=EvaluationDetail)
def get_evaluation(
    evaluation_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    e = db.query(Evaluation).filter(Evaluation.id == evaluation_id).first()
    if not e:
        raise HTTPException(status_code=404, detail="Evaluation not found")
    if current_user.role == "student" and e.resume.uploaded_by != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this evaluation")

    payload = EvaluationResponse.model_validate(e).model_dump()
    payload.update({
        "candidate_name": e.resume.entities.get("name") if e.resume.entities else None,
        "candidate_email": e.resume.email,
        "jd_title": e.jd.title if e.jd else None,
        "jd_location": e.jd.location if e.jd else None,
        "resume_location": e.resume.entities.get("location") if e.resume.entities else None,
        "score_breakdown": {
            "keyword_score": e.keyword_score,
            "semantic_score": e.semantic_score,
            "experience_score": e.experience_score,
            "certification_score": e.certification_score,
        },
    })
    return EvaluationDetail(**payload)


@router.get("/history/mine", response_model=List[EvaluationResponse])
def my_evaluation_history(
    jd_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = (
        db.query(Evaluation)
        .join(Evaluation.resume)
        .filter(Resume.uploaded_by == current_user.id)
    )
    if jd_id:
        query = query.filter(Evaluation.jd_id == jd_id)
    results = query.order_by(Evaluation.evaluated_at.asc()).all()

    out = []
    for e in results:
        item = EvaluationResponse.model_validate(e)
        item.jd_title = e.jd.title if e.jd else None
        out.append(item)
    return out