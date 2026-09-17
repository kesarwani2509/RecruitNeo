import chromadb
from typing import List
from backend.app.config import settings


_client = None


def get_client():
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(path=settings.chroma_persist_dir)
    return _client


def get_or_create_collection(name: str = "resume_jd_embeddings"):
    client = get_client()
    return client.get_or_create_collection(name=name)


def add_document(doc_id: str, embedding: List[float], metadata: dict):
    collection = get_or_create_collection()
    collection.upsert(
        ids=[doc_id],
        embeddings=[embedding],
        metadatas=[metadata],
    )


def query_similar(query_embedding: List[float], n_results: int = 5):
    collection = get_or_create_collection()
    return collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
    )
