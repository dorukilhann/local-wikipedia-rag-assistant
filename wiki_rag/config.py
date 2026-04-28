"""Application configuration for the local Wikipedia RAG assistant."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _env_path(name: str, default: Path) -> Path:
    value = os.getenv(name)
    return Path(value).expanduser().resolve() if value else default


@dataclass(frozen=True)
class AppConfig:
    project_root: Path
    data_dir: Path
    sqlite_path: Path
    chroma_path: Path
    collection_name: str
    ollama_base_url: str
    embed_model: str
    generation_model: str
    chunk_words: int
    chunk_overlap: int
    retrieve_k: int
    generation_timeout: int


def get_config() -> AppConfig:
    data_dir = _env_path("WIKI_RAG_DATA_DIR", PROJECT_ROOT / "data")
    return AppConfig(
        project_root=PROJECT_ROOT,
        data_dir=data_dir,
        sqlite_path=_env_path("WIKI_RAG_SQLITE_PATH", data_dir / "wiki_rag.sqlite3"),
        chroma_path=_env_path("WIKI_RAG_CHROMA_PATH", data_dir / "chroma"),
        collection_name=os.getenv("WIKI_RAG_COLLECTION", "wikipedia_chunks"),
        ollama_base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        embed_model=os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text"),
        generation_model=os.getenv("OLLAMA_GENERATION_MODEL", "llama3.2:3b"),
        chunk_words=int(os.getenv("WIKI_RAG_CHUNK_WORDS", "220")),
        chunk_overlap=int(os.getenv("WIKI_RAG_CHUNK_OVERLAP", "45")),
        retrieve_k=int(os.getenv("WIKI_RAG_RETRIEVE_K", "8")),
        generation_timeout=int(os.getenv("WIKI_RAG_GENERATION_TIMEOUT", "180")),
    )
