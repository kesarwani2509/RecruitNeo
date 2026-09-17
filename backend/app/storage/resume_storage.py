import os
import uuid
from pathlib import Path
from backend.app.config import settings


def save_resume_file(content: bytes, original_filename: str) -> str:
    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)
    ext = os.path.splitext(original_filename)[1]
    unique_name = f"{uuid.uuid4()}{ext}"
    file_path = upload_dir / unique_name
    with open(file_path, "wb") as f:
        f.write(content)
    return str(file_path)
