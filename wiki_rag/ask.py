"""CLI smoke-check interface for the local RAG assistant."""

from __future__ import annotations

import argparse
import sys

from wiki_rag.rag import RAGAssistant


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Ask the local Wikipedia RAG assistant.")
    parser.add_argument("query", help="Question to ask.")
    parser.add_argument(
        "--show-context",
        action="store_true",
        help="Print retrieved chunks after the answer.",
    )
    return parser.parse_args()


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    args = parse_args()
    assistant = RAGAssistant()
    result = assistant.answer(args.query)
    print(result.answer)
    if args.show_context:
        print("\nRetrieved context")
        print("-----------------")
        for chunk in result.retrieved_chunks:
            print(f"{chunk.title} [{chunk.entity_type}] chunk {chunk.chunk_index}")
            print(chunk.source_url)
            print(chunk.text[:700].strip())
            print()


if __name__ == "__main__":
    main()
