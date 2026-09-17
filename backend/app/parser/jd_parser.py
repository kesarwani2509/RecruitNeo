import re
from typing import Dict, List, Optional

try:
    import spacy
    _nlp = spacy.load("en_core_web_sm")
except Exception:
    _nlp = None

SKILL_KEYWORDS = {
    "python", "java", "javascript", "typescript", "c++", "c#", "go", "rust", "ruby",
    "php", "scala", "kotlin", "swift", "sql", "nosql", "mongodb", "postgresql",
    "mysql", "redis", "elasticsearch", "docker", "kubernetes", "aws", "azure",
    "gcp", "terraform", "ansible", "jenkins", "git", "ci/cd", "react", "angular",
    "vue", "node.js", "django", "flask", "fastapi", "spring", "express", "redux",
    "html", "css", "tailwind", "bootstrap", "machine learning", "deep learning",
    "nlp", "tensorflow", "pytorch", "scikit-learn", "pandas", "numpy", "spark",
    "hadoop", "kafka", "rabbitmq", "graphql", "rest", "microservices", "linux",
    "bash", "shell", "agile", "scrum", "jira", "tableau", "power bi", "excel",
    "data analysis", "etl", "airflow", "snowflake", "databricks", "data engineering",
    "devops", "cybersecurity", "penetration testing", "network security",
}

CERT_KEYWORDS = {
    "aws certified", "azure certified", "gcp certified", "cka", "ckad", "pmp",
    "scrum master", "cissp", "ceh", "comptia", "oracle certified",
    "tensorflow certified", "tableau certified", "six sigma",
}

LOCATIONS = {
    "hyderabad", "bangalore", "bengaluru", "pune", "delhi", "delhi ncr",
    "ncr", "chennai", "mumbai", "kolkata", "gurgaon", "gurugram", "noida",
}

def extract_title(text: str) -> Optional[str]:
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    for ln in lines[:10]:
        if any(w in ln.lower() for w in ["engineer", "developer", "analyst",
                                          "manager", "scientist", "consultant",
                                          "intern", "lead", "architect"]):
            return ln[:100]
    return lines[0][:100] if lines else None

def extract_experience(text: str) -> (Optional[int], Optional[int]):
    min_m = re.search(r"(\d+)\s*[-–to]+\s*(\d+)\s*years?", text.lower())
    if min_m:
        return int(min_m.group(1)), int(min_m.group(2))
    single = re.search(r"(\d+)\+?\s*years?", text.lower())
    if single:
        return int(single.group(1)), None
    return None, None

def extract_skills(text: str) -> List[str]:
    found = set()
    lower = text.lower()
    for s in SKILL_KEYWORDS:
        if re.search(r"\b" + re.escape(s) + r"\b", lower):
            found.add(s)
    return sorted(found)

def extract_certs(text: str) -> List[str]:
    found = set()
    lower = text.lower()
    for c in CERT_KEYWORDS:
        if c in lower:
            found.add(c)
    return sorted(found)

def extract_location(text: str) -> Optional[str]:
    lower = text.lower()
    for loc in LOCATIONS:
        if loc in lower:
            return loc.title()
    return None

def parse_jd(
    raw_text: str,
    title: Optional[str] = None,
    company: Optional[str] = None,
    location: Optional[str] = None,
) -> Dict:
    min_exp, max_exp = extract_experience(raw_text)
    skills = extract_skills(raw_text)
    certs = extract_certs(raw_text)
    detected_loc = extract_location(raw_text)
    structured = {
        "title": title or extract_title(raw_text),
        "company": company,
        "location": location or detected_loc,
        "min_experience": min_exp,
        "max_experience": max_exp,
        "required_skills": skills,
        "preferred_skills": [],
        "required_certs": certs,
    }
    return structured
