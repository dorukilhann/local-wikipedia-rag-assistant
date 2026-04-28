"""Retrieval augmented generation orchestration."""

from __future__ import annotations

from dataclasses import dataclass

from wiki_rag.config import AppConfig, get_config
from wiki_rag.hints import EntityHint, find_entity_hints
from wiki_rag.ollama_client import OllamaClient
from wiki_rag.routing import QueryRoute, classify_query
from wiki_rag.storage import SQLiteStore, StoredChunk
from wiki_rag.vector_store import RetrievedChunk, VectorStore


@dataclass(frozen=True)
class RAGAnswer:
    answer: str
    route: QueryRoute
    retrieved_chunks: list[RetrievedChunk]


def build_context(chunks: list[RetrievedChunk], max_chars: int = 12000) -> str:
    parts: list[str] = []
    total = 0
    for number, chunk in enumerate(chunks, start=1):
        header = (
            f"[{number}] Source title: {chunk.title}\n"
            f"Entity type: {chunk.entity_type}\n"
            f"Source URL: {chunk.source_url}\n"
        )
        body = chunk.text.strip()
        block = f"{header}{body}"
        remaining = max_chars - total
        if remaining <= 0:
            break
        if len(block) > remaining:
            block = block[:remaining].rstrip()
        parts.append(block)
        total += len(block)
    return "\n\n".join(parts)


def build_prompt(query: str, chunks: list[RetrievedChunk]) -> str:
    context = build_context(chunks)
    return f"""You are a fully local Wikipedia RAG assistant.

Answer the user using only the retrieved Wikipedia context below.
If the context does not contain the answer, say exactly: I don't know.
Do not use outside knowledge.
Answer in direct prose, not as a copied source label.
For comparison questions, compare the named source titles using only details present in the context.
It is acceptable for a comparison answer to use different facts for each subject when both subjects have context.
When you cite, use only the Wikipedia page title in parentheses, such as (Albert Einstein).
Do not cite chunk numbers, source numbers, URLs, or entity metadata.

Retrieved context:
{context if context else "No relevant context was retrieved."}

User question:
{query}

Grounded answer:"""


class RAGAssistant:
    def __init__(
        self,
        config: AppConfig | None = None,
        ollama_client: OllamaClient | None = None,
        vector_store: VectorStore | None = None,
        sqlite_store: SQLiteStore | None = None,
    ):
        self.config = config or get_config()
        self.ollama = ollama_client or OllamaClient(
            self.config.ollama_base_url, timeout=self.config.generation_timeout
        )
        self.vector_store = vector_store or VectorStore(
            self.config.chroma_path, self.config.collection_name
        )
        self.sqlite_store = sqlite_store or SQLiteStore(self.config.sqlite_path)
        self.sqlite_store.initialize()

    def answer(self, query: str) -> RAGAnswer:
        route = classify_query(query)
        embedding = self.ollama.embed_texts([query], self.config.embed_model)[0]
        entity_filter = route.route if route.route in {"person", "place"} else None
        retrieved = self.vector_store.query(
            query_embedding=embedding,
            n_results=self.config.retrieve_k,
            entity_type=entity_filter,
        )
        retrieved = self._prepend_priority_context(route, query, retrieved)
        if not retrieved:
            return RAGAnswer("I don't know.", route, [])
        prompt = build_prompt(query, retrieved)
        answer = self.ollama.generate(
            prompt,
            self.config.generation_model,
            timeout=self.config.generation_timeout,
        )
        return RAGAnswer(answer or "I don't know.", route, retrieved)

    def _prepend_priority_context(
        self, route: QueryRoute, query: str, chunks: list[RetrievedChunk]
    ) -> list[RetrievedChunk]:
        exact_titles = [
            EntityHint(title=title, reason="matched person name")
            for title in route.matched_people
        ] + [
            EntityHint(title=title, reason="matched place name")
            for title in route.matched_places
        ]
        hinted_titles = find_entity_hints(query)
        priority_titles = [*exact_titles, *hinted_titles]
        if not priority_titles:
            return chunks

        existing_ids = {chunk.chunk_id for chunk in chunks}
        intro_chunks: list[RetrievedChunk] = []
        seen_titles: set[str] = set()
        for hint in priority_titles:
            if hint.title.lower() in seen_titles:
                continue
            seen_titles.add(hint.title.lower())
            for stored in self.sqlite_store.first_chunks_for_title(hint.title, limit=2):
                if stored.chunk_id in existing_ids:
                    continue
                intro_chunks.append(_stored_to_retrieved(stored))
                existing_ids.add(stored.chunk_id)

        return intro_chunks + chunks


def _stored_to_retrieved(chunk: StoredChunk) -> RetrievedChunk:
    return RetrievedChunk(
        chunk_id=chunk.chunk_id,
        text=chunk.text,
        title=chunk.title,
        entity_type=chunk.entity_type,
        source_url=chunk.source_url,
        chunk_index=chunk.chunk_index,
        distance=None,
    )
