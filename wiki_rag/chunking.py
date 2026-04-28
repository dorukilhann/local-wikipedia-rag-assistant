"""Paragraph-aware chunking implemented without RAG framework helpers."""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class TextChunk:
    index: int
    text: str
    word_count: int


def _clean_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _paragraphs(text: str) -> list[str]:
    cleaned = _clean_text(text)
    paragraphs = []
    for paragraph in re.split(r"\n\s*\n", cleaned):
        paragraph = re.sub(r"\s+", " ", paragraph).strip()
        if paragraph:
            paragraphs.append(paragraph)
    return paragraphs


def chunk_text(text: str, chunk_words: int = 220, overlap_words: int = 45) -> list[TextChunk]:
    """Split text into word chunks while trying to preserve paragraph boundaries."""

    if chunk_words <= 0:
        raise ValueError("chunk_words must be positive")
    if overlap_words < 0:
        raise ValueError("overlap_words must be non-negative")
    if overlap_words >= chunk_words:
        raise ValueError("overlap_words must be smaller than chunk_words")

    chunks: list[TextChunk] = []

    def add_chunk(words: list[str]) -> None:
        if not words:
            return
        text_value = " ".join(words).strip()
        chunks.append(TextChunk(index=len(chunks), text=text_value, word_count=len(words)))

    current: list[str] = []
    for paragraph in _paragraphs(text):
        words = paragraph.split()
        if not words:
            continue

        if len(words) > chunk_words:
            add_chunk(current)
            current = []
            step = chunk_words - overlap_words
            start = 0
            while start < len(words):
                window = words[start : start + chunk_words]
                add_chunk(window)
                if start + chunk_words >= len(words):
                    break
                start += step
            continue

        if current and len(current) + len(words) > chunk_words:
            previous = current
            add_chunk(previous)
            overlap = previous[-overlap_words:] if overlap_words else []
            current = overlap + words if len(overlap) + len(words) <= chunk_words else words
        else:
            current.extend(words)

    add_chunk(current)
    return chunks
