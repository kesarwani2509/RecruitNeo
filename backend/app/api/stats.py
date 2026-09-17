from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.app.database import get_db
from backend.app.core.deps import get_current_user
from backend.app.models.user import User
from backend.app.models.evaluation import Evaluation
from backend.app.models.job_description import JobDescription
from backend.app.models.resume import Resume

router = APIRouter(prefix="/api/stats", tags=["stats"])


@router.get("/dashboard")
def dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    total_jds = db.query(func.count(JobDescription.id)).scalar()
    total_resumes = db.query(func.count(Resume.id)).scalar()
    total_evals = db.query(func.count(Evaluation.id)).scalar()

    verdict_counts = dict(
        db.query(Evaluation.fit_verdict, func.count(Evaluation.id))
        .group_by(Evaluation.fit_verdict)
        .all()
    )

    avg_score = db.query(func.avg(Evaluation.relevance_score)).scalar() or 0

    location_dist = {}
    resumes = db.query(Resume).all()
    for r in resumes:
        loc = (r.entities or {}).get("location")
        if loc:
            location_dist[loc] = location_dist.get(loc, 0) + 1

    by_jd = (
        db.query(
            JobDescription.title,
            func.count(Evaluation.id),
            func.avg(Evaluation.relevance_score),
        )
        .join(Evaluation, Evaluation.jd_id == JobDescription.id)
        .group_by(JobDescription.title)
        .all()
    )
    by_jd = [
        {"jd_title": t, "count": c, "avg_score": round(float(a), 1)}
        for t, c, a in by_jd
    ]

    return {
        "total_jds": total_jds,
        "total_resumes": total_resumes,
        "total_evaluations": total_evals,
        "verdict_counts": verdict_counts,
        "avg_score": round(float(avg_score), 1),
        "location_distribution": location_dist,
        "by_jd": by_jd,
    }
