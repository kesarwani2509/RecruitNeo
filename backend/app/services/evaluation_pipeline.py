from sqlalchemy.orm import Session
from backend.app.matcher.keyword_matcher import keyword_score
from backend.app.matcher.semantic_matcher import semantic_similarity
from backend.app.matcher.scorer import experience_score, certification_score, evaluate
from backend.app.matcher.verdict import get_verdict
from backend.app.analyzer.gap_analyzer import analyze_gaps
from backend.app.analyzer.feedback_generator import generate_feedback
from backend.app.models.evaluation import Evaluation
from backend.app.models.job_description import JobDescription
from backend.app.models.resume import Resume


def run_evaluation(db: Session, resume: Resume, jd: JobDescription) -> Evaluation:
    resume_entities = resume.entities or {}
    jd_structured = jd.structured_fields or {}
    kw_score, missing_skills_kw = keyword_score(
        resume_skills=resume_entities.get("skills", []),
        jd_skills=jd_structured.get("required_skills", []),
        resume_text=resume.raw_text or "",
        jd_text=jd.raw_text or "",
    )

    sem_score = semantic_similarity(resume.raw_text or "", jd.raw_text or "")
    exp_score = experience_score(
        candidate_years=resume_entities.get("experience_years"),
        min_exp=jd.min_experience,
        max_exp=jd.max_experience,
    )
    cert_score = certification_score(
        resume_certs=resume_entities.get("certifications", []),
        required_certs=jd_structured.get("required_certs", []),
    )
    scores = evaluate(kw_score, sem_score, exp_score, cert_score)
    final_score = scores["relevance_score"]
    verdict = get_verdict(final_score)
    gaps = analyze_gaps(resume_entities, jd_structured)
    feedback = generate_feedback(
        jd_title=jd.title,
        jd_text=jd.raw_text or "",
        resume_text=resume.raw_text or "",
        gaps=gaps,
        score=final_score,
    )

    evaluation = Evaluation(
        resume_id=resume.id,
        jd_id=jd.id,
        relevance_score=final_score,
        keyword_score=kw_score,
        semantic_score=sem_score,
        experience_score=exp_score,
        certification_score=cert_score,
        fit_verdict=verdict,
        missing_skills=gaps["missing_skills"],
        missing_certs=gaps["missing_certs"],
        missing_projects=gaps["missing_projects"],
        feedback_text=feedback,
    )
    db.add(evaluation)
    db.flush()
    return evaluation
