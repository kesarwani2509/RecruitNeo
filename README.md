<div align="center">

#  RecruitNeo
### AI-Powered Resume Relevance Engine

*Score resumes against job descriptions. Explain the score. Close the feedback loop.*

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-backend-009688?logo=fastapi&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-frontend-FF4B4B?logo=streamlit&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-ORM-D71F00)
![Gemini](https://img.shields.io/badge/Gemini-LLM_feedback-4285F4?logo=googlegemini&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)
![CI](https://github.com/yourusername/recruitneo/workflows/CI/badge.svg)

</div>

---

##  Table of Contents
- [Why RecruitNeo](#-why-recruitneo-is-different)
- [Architecture](#-architecture)
- [Features](#-features)
- [Roles](#-role-based-access)
- [Quick Start](#-quick-start)
- [Docker Deployment](#-docker-deployment)
- [Environment Variables](#-environment-variables)
- [API Reference](#-api-reference)
- [Tech Stack](#-tech-stack)
- [Development](#-development)
- [Contributing](#-contributing)
- [Roadmap](#-roadmap)

---

##  Why RecruitNeo is Different

Most resume screeners hand recruiters an opaque number and stop there. RecruitNeo treats scoring as a **two-sided feedback loop** — recruiters get signal, candidates get a path to improve.

| Capability | RecruitNeo | Typical ATS Tools |
|---|:---:|:---:|
| Explainable, weighted scoring breakdown | ✅ | ❌ |
| Student-facing feedback + score history | ✅ | ❌ |
| Semantic (embedding-based) matching | ✅ | ❌ keyword-only |
| Role-based dashboards (Recruiter/Admin/Student) | ✅ | ⚠️ partial |
| Admin user & role management | ✅ | ❌ |

---

##  Architecture

```
┌─────────────────────┐        HTTP/JWT        ┌──────────────────────┐
│  Streamlit Frontend │ ─────────────────────▶ │   FastAPI Backend     │
│  (role-based UI)    │ ◀───────────────────── │   (auth, scoring)     │
└─────────────────────┘                        └───────────┬──────────┘
                                                              │
                                    ┌─────────────────────────┼─────────────────────────┐
                                    ▼                         ▼                         ▼
                         PostgreSQL / SQLite         Chroma (embeddings)         Local disk
                         users · JDs · evaluations    semantic matching           resume uploads
```

**Data Flow:**
1. **Upload** → Resume (PDF/DOCX) parsed → entities extracted (skills, exp, education, certs, projects)
2. **JD Created** → Parsed for required skills, certs, experience range, location
3. **Evaluation** → Hybrid scoring engine runs (keyword + semantic + experience + certs)
4. **Feedback** → Gap analysis + Gemini LLM generates personalized improvement feedback
5. **Dashboard** → Role-based views: Recruiter/Admin see all, Student sees own history

---

##  Features

### Parsing
- **Resume (PDF/DOCX)** → skills, experience, education, certifications, projects
- **JD** → required skills, certifications, experience range, location

### Hybrid Scoring Engine

| Component | Weight | Method |
|---|:---:|---|
| Hard match | 30% | keyword / fuzzy / TF-IDF |
| Semantic match | 40% | sentence-transformers + cosine similarity |
| Experience fit | 15% | parsed years vs. JD requirement |
| Certification match | 15% | exact + fuzzy cert matching |

### Feedback & Growth
- **Gap analysis**: missing skills, certs, project types
- **Gemini-powered personalized feedback** (template fallback if no API key)
- ** Score-trend tracking** — students see progress across resume re-uploads per job

---

##  Role-Based Access

| Role | Can Do |
|---|---|
| **Recruiter** | Post JDs, review candidates, view evaluations dashboard |
| **Admin** | Everything a recruiter can, plus manage users/roles, org-wide stats |
| **Student** | Upload resume, view own evaluations only, track score improvement |

---

##  Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL 14+ (optional — SQLite works out of the box)
- [Gemini API Key](https://makersuite.google.com/app/apikey) (optional — fallback feedback available)

### Local Development

```bash
# 1. Clone & enter
git clone https://github.com/yourusername/recruitneo.git
cd recruitneo

# 2. Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Download spaCy model
python -m spacy download en_core_web_sm

# 5. Configure environment
cp .env.example .env
# Edit .env with your values (see Environment Variables below)

# 6. Start backend (Terminal 1)
uvicorn backend.app.main:app --reload

# 7. Start frontend (Terminal 2)
streamlit run frontend/dashboard.py
```

**Access:**
- Frontend: http://localhost:8501
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

##  Docker Deployment

### Using Docker Compose (Recommended)

```bash
# 1. Configure environment
cp .env.example .env
# Edit .env with production values

# 2. Build and start all services
docker-compose up -d --build
```

**Services:**
- `postgres` — PostgreSQL 16
- `backend` — FastAPI on port 8000
- `frontend` — Streamlit on port 8500
- `chroma` — Vector DB (optional, for semantic search)

### Manual Docker Build

```bash
# Backend
docker build -t recruitneo-backend -f backend/Dockerfile .

# Frontend
docker build -t recruitneo-frontend -f frontend/Dockerfile .
```

---

##  Environment Variables

| Variable | Required | Default | Description |
|---|:---:|---|---|
| `DATABASE_URL` | No | `sqlite:///./resume_matcher.db` | PostgreSQL: `postgresql://user:pass@host:5432/db` |
| `SECRET_KEY` | **Yes** | — | JWT signing secret (min 32 chars) |
| `ALGORITHM` | No | `HS256` | JWT algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | No | `480` | Token lifetime |
| `GEMINI_API_KEY` | No | — | Google Gemini API key for LLM feedback |
| `UPLOAD_DIR` | No | `./uploads` | Resume upload directory |
| `CHROMA_PERSIST_DIR` | No | `./chroma_db` | Vector store persistence |
| `PROJECT_NAME` | No | `Resume Relevance Check System` | App display name |
| `ENVIRONMENT` | No | `development` | `development` / `production` |

> ** Security**: Never commit `.env` to version control. Use `.env.example` as template.

---

##  API Reference

### Authentication
All endpoints (except `/api/auth/*`) require `Authorization: Bearer <token>` header.

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/auth/register` | Register new user |
| `POST` | `/api/auth/login` | Login, returns JWT |
| `GET` | `/api/auth/me` | Current user profile |

### Job Descriptions
| Method | Endpoint | Roles | Description |
|---|---|---|---|
| `POST` | `/api/jds` | Recruiter, Admin | Create JD |
| `GET` | `/api/jds` | All | List all JDs |
| `GET` | `/api/jds/{id}` | All | Get JD details |
| `DELETE` | `/api/jds/{id}` | Owner, Admin | Delete JD |

### Resumes
| Method | Endpoint | Roles | Description |
|---|---|---|---|
| `POST` | `/api/resumes/upload` | All | Upload resume + optional JD evaluation |
| `GET` | `/api/resumes` | Recruiter, Admin | List all resumes |
| `GET` | `/api/resumes/{id}` | Owner, Admin | Get resume details |

### Evaluations
| Method | Endpoint | Roles | Description |
|---|---|---|---|
| `GET` | `/api/evaluations` | Recruiter, Admin | List evaluations (with filters) |
| `GET` | `/api/evaluations/{id}` | Owner, Admin | Get evaluation detail |
| `GET` | `/api/evaluations/history/mine` | Student | Own evaluation history |

### Admin
| Method | Endpoint | Roles | Description |
|---|---|---|---|
| `GET` | `/api/admin/users` | Admin | List all users |
| `PATCH` | `/api/admin/users/{id}` | Admin | Update user role |
| `DELETE` | `/api/admin/users/{id}` | Admin | Delete user (not self) |
| `GET` | `/api/admin/stats` | Admin | Organization statistics |

**Full OpenAPI spec:** `GET /openapi.json` or visit `/docs` when running.

---

##  Tech Stack

| Layer | Technologies |
|---|---|
| **API** | FastAPI, Uvicorn, Pydantic, SQLAlchemy, Alembic |
| **Auth** | python-jose (JWT), passlib (bcrypt) |
| **Parsing** | PyMuPDF, python-docx, spaCy (en_core_web_sm) |
| **Matching** | sentence-transformers, scikit-learn, rank-bm25, rapidfuzz |
| **Vector Store** | ChromaDB |
| **LLM** | Google Gemini (google-genai) |
| **Frontend** | Streamlit, Plotly, Pandas |
| **DB** | PostgreSQL (prod), SQLite (dev) |
| **Testing** | pytest, pytest-asyncio, httpx |
| **Quality** | ruff, mypy, pre-commit |

---

##  Development

### Install Dev Dependencies
```bash
pip install -e ".[dev]"
# Or manually:
pip install ruff mypy pytest pytest-asyncio httpx pre-commit
pre-commit install
```

### Code Quality Commands
```bash
# Lint + auto-fix
ruff check --fix backend/ frontend/ tests/
ruff format backend/ frontend/ tests/

# Type check
mypy backend/ frontend/ --config-file pyproject.toml

# Run tests
pytest tests/ -v --tb=short

# Run with coverage
pytest --cov=backend --cov=frontend --cov-report=html
```

### Database Migrations
```bash
# Create new migration
cd backend && alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

---

##  Contributing

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feat/amazing-feature`
3. **Commit** changes: `git commit -m 'feat: add amazing feature'`
4. **Push** to branch: `git push origin feat/amazing-feature`
5. **Open** a Pull Request

### Commit Message Convention
We follow [Conventional Commits](https://www.conventionalcommits.org/):
- `feat:` — new feature
- `fix:` — bug fix
- `docs:` — documentation
- `refactor:` — code restructure
- `test:` — test additions
- `chore:` — maintenance

### Code Style
- **Formatter**: Ruff (line-length 100, double quotes)
- **Linter**: Ruff (pycodestyle, pyflakes, isort, bugbear)
- **Types**: MyPy (strict mode for new code)
- **Pre-commit**: Runs on every commit

---

##  Roadmap

- [ ] AI-generated resume rewrite suggestions
- [ ] Recruiter shortlist & candidate notes
- [ ] JD quality scoring
- [ ] Email verification on signup
- [ ] Shareable candidate score badge
- [ ] Multi-language resume support
- [ ] Webhook notifications for evaluation completion
- [ ] Advanced analytics dashboard

---

##  License

Distributed under the MIT License. See `LICENSE` for more information.

---

##  Acknowledgments

- [sentence-transformers](https://www.sbert.net/) for semantic embeddings
- [ChromaDB](https://www.trychroma.com/) for vector storage
- [spaCy](https://spacy.io/) for NLP parsing
- [Google Gemini](https://ai.google.dev/) for LLM feedback
- [Streamlit](https://streamlit.io/) for the beautiful frontend framework

---

<div align="center">
Built for recruiters, admins, and the candidates trying to land the job.
</div>