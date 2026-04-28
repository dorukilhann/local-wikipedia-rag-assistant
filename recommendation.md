# Production Deployment Recommendation

This project is designed for localhost coursework, but the same architecture can be hardened for production.

## Recommended Architecture
- Keep ingestion as a separate scheduled job with retry logic and source version tracking.
- Store raw documents in a managed relational database such as PostgreSQL.
- Use a production vector database or managed Chroma-compatible service if multiple users need concurrent access.
- Serve the RAG pipeline behind an API service with authentication, rate limits, request logging, and health checks.
- Run local or self-hosted models on dedicated GPU nodes when privacy is required.

## Reliability Improvements
- Add document freshness checks against Wikipedia revision IDs.
- Add automatic evaluation sets for retrieval quality and answer groundedness.
- Track latency for embedding, retrieval, and generation separately.
- Add backup and restore procedures for the document database and vector index.

## Security and Privacy
- Keep external LLM APIs disabled unless users explicitly opt in.
- Sanitize logs so user questions and retrieved context are not exposed unnecessarily.
- Restrict reset and ingestion actions to trusted users in a multi-user deployment.

## Tradeoffs
- Small local models are inexpensive and private, but may produce weaker summaries than larger hosted models.
- Larger local models improve reasoning quality but require more memory and slower inference.
- A single vector collection is simple and works well here; very large deployments may benefit from separate indexes or hybrid lexical/vector search.
