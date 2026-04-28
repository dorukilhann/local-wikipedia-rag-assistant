"""Chroma vector storage with assignment metadata filters."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from wiki_rag.storage import StoredChunk


@dataclass(frozen=True)
class RetrievedChunk:
    chunk_id: str
    text: str
    title: str
    entity_type: str
    source_url: str
    chunk_index: int
    distance: float | None


class VectorStore:
    def __init__(self, path: Path, collection_name: str):
        try:
            import chromadb
        except ImportError as exc:
            raise RuntimeError(
                "chromadb is not installed. Run `pip install -r requirements.txt`."
            ) from exc

        self.path = path
        self.collection_name = collection_name
        self.path.mkdir(parents=True, exist_ok=True)
        self.client = chromadb.PersistentClient(path=str(self.path))
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"},
        )

    def reset(self) -> None:
        try:
            self.client.delete_collection(self.collection_name)
        except Exception:
            pass
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"},
        )

    def delete_title(self, title: str) -> None:
        try:
            self.collection.delete(where={"title": title})
        except Exception:
            pass

    def upsert_chunks(self, chunks: list[StoredChunk], embeddings: list[list[float]]) -> None:
        if not chunks:
            return
        if len(chunks) != len(embeddings):
            raise ValueError("chunks and embeddings must have the same length")
        self.collection.upsert(
            ids=[chunk.chunk_id for chunk in chunks],
            embeddings=embeddings,
            documents=[chunk.text for chunk in chunks],
            metadatas=[
                {
                    "entity_type": chunk.entity_type,
                    "title": chunk.title,
                    "source_url": chunk.source_url,
                    "chunk_index": chunk.chunk_index,
                }
                for chunk in chunks
            ],
        )

    def query(
        self, query_embedding: list[float], n_results: int, entity_type: str | None = None
    ) -> list[RetrievedChunk]:
        where = {"entity_type": entity_type} if entity_type in {"person", "place"} else None
        result = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=where,
            include=["documents", "metadatas", "distances"],
        )
        return self._parse_query_result(result)

    @staticmethod
    def _parse_query_result(result: dict[str, Any]) -> list[RetrievedChunk]:
        ids = result.get("ids", [[]])[0]
        documents = result.get("documents", [[]])[0]
        metadatas = result.get("metadatas", [[]])[0]
        distances = result.get("distances", [[]])[0]
        chunks: list[RetrievedChunk] = []
        for index, chunk_id in enumerate(ids):
            metadata = metadatas[index] or {}
            chunks.append(
                RetrievedChunk(
                    chunk_id=chunk_id,
                    text=documents[index],
                    title=str(metadata.get("title", "")),
                    entity_type=str(metadata.get("entity_type", "")),
                    source_url=str(metadata.get("source_url", "")),
                    chunk_index=int(metadata.get("chunk_index", 0)),
                    distance=distances[index] if index < len(distances) else None,
                )
            )
        return chunks
