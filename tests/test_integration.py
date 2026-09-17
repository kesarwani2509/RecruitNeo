import os
import sys
import time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.database import init_db, SessionLocal
from backend.app.models.evaluation import Evaluation
init_db()

client = TestClient(app)
unique_email = f"recruiter_{int(time.time())}@test.com"

# Register
r = client.post("/api/auth/register", json={
    "name": "Test Recruiter",
    "email": unique_email,
    "password": "password123",
    "role": "recruiter",
    "location": "Bangalore",
})
assert r.status_code == 200, r.text
token = r.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}
print("✓ Register + login OK")

# Create JD
with open("tests/fixtures/sample_jd.txt") as f:
    jd_text = f.read()
r = client.post("/api/jds", json={
    "title": "Senior Data Scientist",
    "company": "Acme Corp",
    "location": "Bangalore",
    "raw_text": jd_text,
}, headers=headers)
assert r.status_code == 200, r.text
jd = r.json()
jd_id = jd["id"]
print("✓ JD created:", jd["structured_fields"].get("title"))
print("  Parsed skills:", jd["structured_fields"].get("required_skills"))
print("  Parsed certs:", jd["structured_fields"].get("required_certs"))

# Upload resume
with open("tests/fixtures/sample_resume.docx", "rb") as f:
    files = {"file": ("sample_resume.docx", f, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
    data = {"jd_id": jd_id, "candidate_name": "John Doe", "location": "Bangalore"}
    r = client.post("/api/resumes/upload", files=files, data=data, headers=headers)
assert r.status_code == 200, r.text
evals = r.json()
print(f"✓ Resume uploaded, {len(evals)} evaluation(s) generated")
e = evals[0]
print(f"  Relevance Score: {e['relevance_score']}/100")
print(f"  Verdict: {e['fit_verdict']}")
print(f"  Keyword: {e['keyword_score']}, Semantic: {e['semantic_score']}, "
      f"Exp: {e['experience_score']}, Cert: {e['certification_score']}")
print(f"  Missing Skills: {e['missing_skills']}")
print(f"  Missing Certs: {e['missing_certs']}")
print(f"  Feedback: {e['feedback_text'][:150]}...")

# List evaluations
r = client.get("/api/evaluations", headers=headers)
assert r.status_code == 200
print(f"✓ Listed {len(r.json())} evaluation(s)")

# Stats
r = client.get("/api/stats/dashboard", headers=headers)
assert r.status_code == 200
print("✓ Dashboard stats:", r.json())
print("\n=== ALL INTEGRATION TESTS PASSED ===")
