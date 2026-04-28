"""Command-line ingestion for Wikipedia documents, SQLite, and Chroma."""

from __future__ import annotations

import argparse
from collections.abc import Iterable

from wiki_rag.chunking import chunk_text
from wiki_rag.config import AppConfig, get_config
from wiki_rag.entities import Entity, all_entities
from wiki_rag.ollama_client import OllamaClient
from wiki_rag.storage import SQLiteStore, StoredChunk
from wiki_rag.vector_store import VectorStore
from wiki_rag.wiki_client import fetch_wikipedia_page


def batch_items(items: list[StoredChunk], batch_size: int) -> Iterable[list[StoredChunk]]:
    for start in range(0, len(items), batch_size):
        yield items[start : start + batch_size]


def ingest_entities(config: AppConfig, entities: list[Entity], reset: bool = False) -> tuple[int, int]:
    store = SQLiteStore(config.sqlite_path)
    store.initialize()
    vector_store = VectorStore(config.chroma_path, config.collection_name)
    ollama = OllamaClient(config.ollama_base_url, timeout=config.generation_timeout)

    if reset:
        print("Resetting SQLite rows and Chroma collection...")
        store.reset()
        vector_store.reset()

    run_id = store.begin_run(reset=reset)
    document_count = 0
    chunk_count = 0

    for entity in entities:
        print(f"Fetching {entity.entity_type}: {entity.title}")
        document = fetch_wikipedia_page(entity.title)
        chunks = chunk_text(
            document.content,
            chunk_words=config.chunk_words,
            overlap_words=config.chunk_overlap,
        )
        store_title = entity.title
        store.upsert_document(
            title=store_title,
            entity_type=entity.entity_type,
            source_url=document.source_url,
            content=document.content,
        )
        stored_chunks = store.replace_chunks_for_document(
            title=store_title,
            entity_type=entity.entity_type,
            source_url=document.source_url,
            chunks=chunks,
        )

        vector_store.delete_title(store_title)
        for batch in batch_items(stored_chunks, batch_size=16):
            embeddings = ollama.embed_texts([chunk.text for chunk in batch], config.embed_model)
            vector_store.upsert_chunks(batch, embeddings)

        document_count += 1
        chunk_count += len(stored_chunks)
        print(f"Stored {len(stored_chunks)} chunks for {store_title}")

    store.finish_run(run_id, document_count=document_count, chunk_count=chunk_count)
    return document_count, chunk_count


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Ingest Wikipedia pages into local RAG storage.")
    parser.add_argument("--reset", action="store_true", help="Clear local SQLite and Chroma data first.")
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Ingest only the first N entities, useful for a quick smoke test.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = get_config()
    entities = all_entities()[: args.limit] if args.limit else all_entities()
    docs, chunks = ingest_entities(config=config, entities=entities, reset=args.reset)
    print(f"Finished ingestion: {docs} documents, {chunks} chunks")


if __name__ == "__main__":
    main()
