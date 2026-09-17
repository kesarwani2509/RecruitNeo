from typing import List
from sentence_transformers import SentenceTransformer
import numpy as np

_model = None

def get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    return _model

def embed(texts: List[str]) -> np.ndarray:
    model = get_model()
    return model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)

def semantic_similarity(resume_text: str, jd_text: str) -> float:
    if not resume_text.strip() or not jd_text.strip():
        return 0.0
    embeddings = embed([resume_text, jd_text])
    sim = np.dot(embeddings[0], embeddings[1])
    return round(float(sim), 4)
