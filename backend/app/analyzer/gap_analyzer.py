from typing import Dict, List
from rapidfuzz import fuzz


def _is_missing(item: str, present: List[str], threshold: int = 80) -> bool:
    q = item.lower().strip()
    for p in present:
        if fuzz.token_sort_ratio(q, p.lower().strip()) >= threshold:
            return False
    return True


def analyze_gaps(
    resume_entities: Dict,
    jd_structured: Dict,
) -> Dict[str, List[str]]:
    resume_skills = [s.lower() for s in resume_entities.get("skills", [])]
    resume_certs = [c.lower() for c in resume_entities.get("certifications", [])]
    resume_projects = resume_entities.get("projects", [])

    missing_skills = [
        s for s in jd_structured.get("required_skills", [])
        if _is_missing(s, resume_skills)
    ]
    missing_certs = [
        c for c in jd_structured.get("required_certs", [])
        if _is_missing(c, resume_certs)
    ]

    jd_text = jd_structured.get("title", "").lower()
    missing_projects = []
    proj_terms = ["api", "ml model", "dashboard", "web app", "data pipeline",
                  "microservice", "etl", "automation", "mobile app"]
    for term in proj_terms:
        if term in jd_text and not any(term in p.lower() for p in resume_projects):
            missing_projects.append(term)

    return {
        "missing_skills": missing_skills,
        "missing_certs": missing_certs,
        "missing_projects": missing_projects,
    }
