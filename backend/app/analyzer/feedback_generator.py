from google import genai
from google.genai import types
from typing import Dict, List
from backend.app.config import settings


def generate_feedback(
    jd_title: str,
    jd_text: str,
    resume_text: str,
    gaps: Dict[str, List[str]],
    score: int,
) -> str:
    if not settings.gemini_api_key:
        return _template_feedback(gaps, score)

    try:
        client = genai.Client(api_key=settings.gemini_api_key)

        missing_skills = ", ".join(gaps.get("missing_skills", [])) or "None"
        missing_certs = ", ".join(gaps.get("missing_certs", [])) or "None"
        missing_projects = ", ".join(gaps.get("missing_projects", [])) or "None"

        prompt = f"""You are a career coach helping a student improve their resume.
Job Role: {jd_title}
Resume Relevance Score: {score}/100

Job Description (excerpt):
{jd_text[:2500]}

Resume (excerpt):
{resume_text[:2500]}

Gaps identified:
- Missing Skills: {missing_skills}
- Missing Certifications: {missing_certs}
- Missing Project Types: {missing_projects}

Provide 3-5 specific, actionable suggestions for the student to improve their resume
for this role. Be encouraging but direct. Use bullet points."""

        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(temperature=0.4),
        )
        return response.text.strip()
    except Exception:
        return _template_feedback(gaps, score)


def _template_feedback(gaps: Dict[str, List[str]], score: int) -> str:
    lines = [f"Your resume scored {score}/100 for this role. Here's how to improve:"]
    if gaps.get("missing_skills"):
        lines.append(f"- Develop or highlight these skills: {', '.join(gaps['missing_skills'])}.")
    if gaps.get("missing_certs"):
        lines.append(f"- Pursue these certifications: {', '.join(gaps['missing_certs'])}.")
    if gaps.get("missing_projects"):
        lines.append(f"- Add projects demonstrating: {', '.join(gaps['missing_projects'])}.")
    lines.append("- Use clear section headings and quantify achievements with metrics.")
    return "\n".join(lines)
