from typing import Dict, List, Optional

WEIGHTS = {
    "keyword": 0.30,
    "semantic": 0.40,
    "experience": 0.15,
    "certification": 0.15,
}

def experience_score(
    candidate_years: Optional[int],
    min_exp: Optional[int],
    max_exp: Optional[int],
) -> float:
    if candidate_years is None:
        return 0.0
    if min_exp is None and max_exp is None:
        return 1.0
    if min_exp is not None and candidate_years >= min_exp:
        if max_exp is None or candidate_years <= max_exp:
            return 1.0
        over = candidate_years - max_exp
        return max(0.5, 1.0 - over * 0.1)
    if min_exp is not None:
        gap = min_exp - candidate_years
        return max(0.0, 1.0 - gap * 0.2)
    return 1.0

def certification_score(
    resume_certs: List[str],
    required_certs: List[str],
) -> float:
    if not required_certs:
        return 1.0
    req_set = {c.lower() for c in required_certs}
    matched = sum(1 for c in resume_certs if c.lower() in req_set)
    return matched / len(required_certs)

def compute_final_score(
    keyword: float,
    semantic: float,
    exp: float,
    cert: float,
) -> int:
    final = (
        WEIGHTS["keyword"] * keyword
        + WEIGHTS["semantic"] * semantic
        + WEIGHTS["experience"] * exp
        + WEIGHTS["certification"] * cert
    )
    return int(round(final * 100))

def evaluate(
    keyword: float,
    semantic: float,
    exp: float,
    cert: float,
) -> Dict:
    score = compute_final_score(keyword, semantic, exp, cert)
    return {
        "keyword_score": round(keyword, 4),
        "semantic_score": round(semantic, 4),
        "experience_score": round(exp, 4),
        "certification_score": round(cert, 4),
        "relevance_score": score,
    }
