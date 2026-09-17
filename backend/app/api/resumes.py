from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session
from typing import List, Optional
from backend.app.database import get_db
from backend.app.core.deps import get_current_user
from backend.app.models.user import User
from backend.app.models.resume import Resume
from backend.app.models.job_description import JobDescription
from backend.app.schemas.resume import ResumeResponse
from backend.app.schemas.evaluation import EvaluationResponse
from backend.app.storage.resume_storage import save_resume_file
from backend.app.parser.resume_parser import parse_resume
from backend.app.services.evaluation_pipeline import run_evaluation

router = APIRouter(prefix="/api/resumes", tags=["resumes"])


@router.post("/upload", response_model=List[EvaluationResponse])
async def upload_resume(
    file: UploadFile = File(...),
    jd_id: Optional[str] = Form(None),
    candidate_name: Optional[str] = Form(None),
    location: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not file.filename.lower().endswith((".pdf", ".docx", ".doc")):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF and DOCX files are supported",
        )

    content = await file.read()
    file_path = save_resume_file(content, file.filename)

    parsed = parse_resume(file_path, candidate_location=location)
    entities = parsed["entities"]
    if candidate_name:
        entities["name"] = candidate_name

    resume = Resume(
        filename=file.filename,
        file_path=file_path,
        candidate_name=entities.get("name"),
        email=entities.get("email"),
        phone=entities.get("phone"),
        location=entities.get("location"),
        raw_text=parsed["raw_text"],
        entities=entities,
        uploaded_by=current_user.id,
    )
    db.add(resume)
    db.flush()

    if jd_id:
        jd = db.query(JobDescription).filter(JobDescription.id == jd_id).first()
        if not jd:
            raise HTTPException(status_code=404, detail="JD not found")
        evaluation = run_evaluation(db, resume, jd)
        db.commit()
        return [EvaluationResponse.model_validate(evaluation)]

    jds = db.query(JobDescription).all()
    evaluations = [run_evaluation(db, resume, jd) for jd in jds]
    db.commit()
    return [EvaluationResponse.model_validate(e) for e in evaluations]


@router.get("", response_model=List[ResumeResponse])
def list_resumes(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    resumes = db.query(Resume).order_by(Resume.created_at.desc()).all()
    return resumes
