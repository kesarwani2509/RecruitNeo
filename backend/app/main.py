from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.api import auth, jds, resumes, evaluations, stats, admin
from backend.app.config import settings
from backend.app.database import init_db

app = FastAPI(title=settings.project_name)

@app.on_event("startup")
def on_startup():
    init_db()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth.router)
app.include_router(jds.router)
app.include_router(resumes.router)
app.include_router(evaluations.router)
app.include_router(stats.router)
app.include_router(admin.router)

@app.get("/")
def root():
    return {"message": settings.project_name, "status": "running"}

@app.get("/health")
def health():
    return {"status": "ok"}