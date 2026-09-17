import re
from typing import List, Tuple
from rapidfuzz import fuzz
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def normalize(text: str) -> str:
    return re.sub(r"[^a-z0-9+\s.#/]", " ", text.lower()).strip()


def fuzzy_skill_match(resume_skills: List[str], jd_skills: List[str], threshold: int = 80) -> Tuple[float, List[str]]:
    if not jd_skills:
        return 1.0, []
    matched = 0
    matched_skills = []
    for jd_skill in jd_skills:
        js = normalize(jd_skill)
        best = 0
        for r_skill in resume_skills:
            rs = normalize(r_skill)
            score = fuzz.token_sort_ratio(js, rs)
            best = max(best, score)
        if best >= threshold:
            matched += 1
            matched_skills.append(jd_skill)
    score = matched / len(jd_skills)
    missing = [s for s in jd_skills if s not in matched_skills]
    return score, missing


def tfidf_similarity(resume_text: str, jd_text: str) -> float:
    if not resume_text.strip() or not jd_text.strip():
        return 0.0
    vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
    try:
        tfidf = vectorizer.fit_transform([resume_text, jd_text])
        sim = cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0]
    except ValueError:
        return 0.0
    return float(sim)


def keyword_score(
    resume_skills: List[str],
    jd_skills: List[str],
    resume_text: str = "",
    jd_text: str = "",
) -> Tuple[float, List[str]]:
    fuzzy, missing = fuzzy_skill_match(resume_skills, jd_skills)
    tfidf = tfidf_similarity(resume_text, jd_text)
    combined = 0.7 * fuzzy + 0.3 * tfidf
    return round(combined, 4), missing
