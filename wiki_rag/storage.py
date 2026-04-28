"""SQLite persistence for raw Wikipedia documents and generated chunks."""

from __future__ import annotations

import hashlib
import re
import sqlite3
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from wiki_rag.chunking import TextChunk


@dataclass(frozen=True)
class StoredChunk:
    chunk_id: str
    title: str
    entity_type: str
    source_url: str
    chunk_index: int
    text: str
    word_count: int


def utc_now() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "chunk"


def make_chunk_id(title: str, chunk: TextChunk) -> str:
    digest = hashlib.sha1(chunk.text.encode("utf-8")).hexdigest()[:12]
    return f"{slugify(title)}-{chunk.index:04d}-{digest}"


class SQLiteStore:
    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        return conn

    def initialize(self) -> None:
        with self.connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS documents (
                    title TEXT PRIMARY KEY,
                    entity_type TEXT NOT NULL,
                    source_url TEXT NOT NULL,
                    content TEXT NOT NULL,
                    fetched_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS chunks (
                    chunk_id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    entity_type TEXT NOT NULL,
                    source_url TEXT NOT NULL,
                    chunk_index INTEGER NOT NULL,
                    text TEXT NOT NULL,
                    word_count INTEGER NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (title) REFERENCES documents(title)
                );

                CREATE TABLE IF NOT EXISTS ingestion_runs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    started_at TEXT NOT NULL,
                    finished_at TEXT,
                    document_count INTEGER DEFAULT 0,
                    chunk_count INTEGER DEFAULT 0,
                    reset INTEGER DEFAULT 0
                );
                """
            )

    def reset(self) -> None:
        with self.connect() as conn:
            conn.execute("DELETE FROM chunks")
            conn.execute("DELETE FROM documents")
            conn.execute("DELETE FROM ingestion_runs")

    def begin_run(self, reset: bool) -> int:
        with self.connect() as conn:
            cursor = conn.execute(
                "INSERT INTO ingestion_runs (started_at, reset) VALUES (?, ?)",
                (utc_now(), int(reset)),
            )
            return int(cursor.lastrowid)

    def finish_run(self, run_id: int, document_count: int, chunk_count: int) -> None:
        with self.connect() as conn:
            conn.execute(
                """
                UPDATE ingestion_runs
                SET finished_at = ?, document_count = ?, chunk_count = ?
                WHERE id = ?
                """,
                (utc_now(), document_count, chunk_count, run_id),
            )

    def upsert_document(
        self, title: str, entity_type: str, source_url: str, content: str
    ) -> None:
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO documents (title, entity_type, source_url, content, fetched_at)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(title) DO UPDATE SET
                    entity_type = excluded.entity_type,
                    source_url = excluded.source_url,
                    content = excluded.content,
                    fetched_at = excluded.fetched_at
                """,
                (title, entity_type, source_url, content, utc_now()),
            )

    def replace_chunks_for_document(
        self, title: str, entity_type: str, source_url: str, chunks: list[TextChunk]
    ) -> list[StoredChunk]:
        stored = [
            StoredChunk(
                chunk_id=make_chunk_id(title, chunk),
                title=title,
                entity_type=entity_type,
                source_url=source_url,
                chunk_index=chunk.index,
                text=chunk.text,
                word_count=chunk.word_count,
            )
            for chunk in chunks
        ]
        with self.connect() as conn:
            conn.execute("DELETE FROM chunks WHERE title = ?", (title,))
            conn.executemany(
                """
                INSERT INTO chunks (
                    chunk_id, title, entity_type, source_url, chunk_index,
                    text, word_count, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        chunk.chunk_id,
                        chunk.title,
                        chunk.entity_type,
                        chunk.source_url,
                        chunk.chunk_index,
                        chunk.text,
                        chunk.word_count,
                        utc_now(),
                    )
                    for chunk in stored
                ],
            )
        return stored

    def count_documents(self) -> int:
        with self.connect() as conn:
            row = conn.execute("SELECT COUNT(*) AS count FROM documents").fetchone()
            return int(row["count"])

    def count_chunks(self) -> int:
        with self.connect() as conn:
            row = conn.execute("SELECT COUNT(*) AS count FROM chunks").fetchone()
            return int(row["count"])

    def first_chunks_for_title(self, title: str, limit: int = 2) -> list[StoredChunk]:
        with self.connect() as conn:
            rows = conn.execute(
                """
                SELECT chunk_id, title, entity_type, source_url, chunk_index, text, word_count
                FROM chunks
                WHERE lower(title) = lower(?)
                ORDER BY chunk_index
                LIMIT ?
                """,
                (title, limit),
            ).fetchall()
        return [
            StoredChunk(
                chunk_id=row["chunk_id"],
                title=row["title"],
                entity_type=row["entity_type"],
                source_url=row["source_url"],
                chunk_index=int(row["chunk_index"]),
                text=row["text"],
                word_count=int(row["word_count"]),
            )
            for row in rows
        ]
