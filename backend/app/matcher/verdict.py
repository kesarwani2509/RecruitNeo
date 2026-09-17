from typing import Dict

def get_verdict(score: int) -> str:
    if score >= 71:
        return "High"
    elif score >= 41:
        return "Medium"
    return "Low"

def verdict_detail(score: int) -> Dict:
    return {
        "relevance_score": score,
        "fit_verdict": get_verdict(score),
    }
