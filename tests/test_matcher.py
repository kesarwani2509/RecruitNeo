import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.app.matcher.scorer import (
    experience_score,
    certification_score,
    compute_final_score,
    evaluate,
)
from backend.app.matcher.verdict import get_verdict
from backend.app.matcher.keyword_matcher import keyword_score, fuzzy_skill_match
from backend.app.analyzer.gap_analyzer import analyze_gaps

def test_experience_score():
    assert experience_score(5, 3, 7) == 1.0
    assert experience_score(2, 5, None) < 1.0
    assert experience_score(None, 3, 5) == 0.0
    assert experience_score(10, None, None) == 1.0

def test_certification_score():
    assert certification_score(["aws certified"], ["aws certified"]) == 1.0
    assert certification_score(["aws certified"], ["aws certified", "pmp"]) == 0.5
    assert certification_score([], []) == 1.0

def test_compute_final_score_bounds():
    s = compute_final_score(1.0, 1.0, 1.0, 1.0)
    assert s == 100
    s2 = compute_final_score(0.0, 0.0, 0.0, 0.0)
    assert s2 == 0

def test_verdict_boundaries():
    assert get_verdict(100) == "High"
    assert get_verdict(71) == "High"
    assert get_verdict(70) == "Medium"
    assert get_verdict(41) == "Medium"
    assert get_verdict(40) == "Low"
    assert get_verdict(0) == "Low"

def test_evaluate_returns_all_components():
    res = evaluate(0.5, 0.6, 0.8, 0.5)
    assert "relevance_score" in res
    assert 0 <= res["relevance_score"] <= 100
    assert res["keyword_score"] == 0.5

def test_fuzzy_skill_match_with_typo():
    score, missing = fuzzy_skill_match(
        ["pythn", "sql", "machine learning"],
        ["python", "sql", "machine learning"],
    )
    assert score >= 0.99
    assert missing == []

def test_keyword_score_combines_fuzzy_and_tfidf():
    score, missing = keyword_score(
        ["python", "sql"],
        ["python", "sql", "docker"],
        resume_text="Experienced python and sql developer",
        jd_text="Looking for python sql docker engineer",
    )
    assert 0.0 <= score <= 1.0
    assert "docker" in missing

def test_gap_analyzer_finds_missing():
    resume = {
        "skills": ["python", "sql"],
        "certifications": [],
        "projects": ["built an api"],
    }
    jd = {
        "required_skills": ["python", "sql", "docker", "kubernetes"],
        "required_certs": ["aws certified"],
    }
    gaps = analyze_gaps(resume, jd)
    assert "docker" in gaps["missing_skills"]
    assert "kubernetes" in gaps["missing_skills"]
    assert "aws certified" in gaps["missing_certs"]
