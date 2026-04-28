# Product PRD: Local Wikipedia RAG Assistant

## Purpose
Build a fully local retrieval augmented generation assistant that answers questions about famous people and famous places from locally stored Wikipedia content.

## Users
The primary user is an instructor or evaluator who wants to run the project on localhost, ingest Wikipedia data, and ask questions through a simple chat interface.

## Core Requirements
- Ingest at least 30 famous people and 30 famous places from Wikipedia.
- Store raw documents and chunks locally in SQLite.
- Split large documents into paragraph-aware chunks with overlap.
- Generate embeddings locally with Ollama `nomic-embed-text`.
- Store vectors in one persistent Chroma collection with metadata filters.
- Route queries to person, place, or both categories using simple rules.
- Use local hints to improve broad location and association questions.
- Generate grounded answers locally with Ollama `llama3.2:3b`.
- Return `I don't know` when retrieved context does not contain the answer.
- Provide Streamlit chat UI and CLI smoke-check command.

## Success Criteria
- `python -m wiki_rag.ingest --reset` builds the local SQLite and Chroma stores.
- `streamlit run app.py` starts a localhost chat interface.
- Required example questions about people, places, and mixed comparisons produce grounded answers.
- Failure cases such as `Who is the president of Mars?` are refused when unsupported by context.
- The repository includes clear setup, run, demo, and deployment documentation.

## Technical Decisions
- Python is used for the app and ingestion pipeline.
- Ollama is used directly over local HTTP; no external LLM API is used.
- Chroma is used as the vector database because it is lightweight, local, and assignment-approved.
- SQLite stores raw text and chunk metadata so the vector store can be rebuilt or inspected.
- One Chroma collection is used with `entity_type` metadata to keep mixed and comparison queries simple.
- Local hint maps are used only to select candidate pages for broad questions; generated answers still must be grounded in retrieved Wikipedia chunks.

## Limitations
- Wikipedia ingestion requires internet access at indexing time.
- Runtime question answering is local after data and models are available.
- Answer quality depends on local model size and retrieved chunks.
- The router is intentionally simple and rule-based for assignment clarity.
