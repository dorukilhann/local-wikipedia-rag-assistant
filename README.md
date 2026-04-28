# Local Wikipedia RAG Assistant

A fully local Wikipedia retrieval augmented generation assistant for the BLG483E Project 3 assignment. It ingests Wikipedia pages for famous people and places, chunks them, embeds them locally with Ollama, stores vectors in Chroma, and answers questions through a Streamlit chat UI.

No external LLM API is used. Wikipedia is contacted only during ingestion so the source pages can be stored locally.

## Features

- 30 famous people and 30 famous places from the assignment plan.
- Paragraph-aware chunking with overlap for large documents.
- Local embeddings through Ollama `nomic-embed-text`.
- Local generation through Ollama `llama3.2:3b`.
- One Chroma vector store with `person` and `place` metadata filters.
- SQLite storage for raw Wikipedia documents and chunks.
- Streamlit chat UI with retrieved context display, clear chat, and reset controls.
- CLI smoke-check command for quick testing.

## Requirements

- Python 3.11 or newer.
- [Ollama](https://ollama.com/) installed and running locally.
- Enough disk space for the Ollama models and local Chroma/SQLite data.

## Setup

Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Install and start Ollama, then pull the local models:

```powershell
ollama pull llama3.2:3b
ollama pull nomic-embed-text
```

Ollama serves its local HTTP API at `http://localhost:11434` by default.

## Ingest Wikipedia Data

Build the local SQLite database and Chroma vector store:

```powershell
python -m wiki_rag.ingest --reset
```

For a quick connectivity smoke test, ingest only the first few entities:

```powershell
python -m wiki_rag.ingest --reset --limit 3
```

Generated local data is stored under `data/` and is intentionally ignored by git.

If you change `wiki_rag/entities.py`, rebuild the index with `python -m wiki_rag.ingest --reset` so SQLite and Chroma match the source code.

## Run the Chat App

```powershell
streamlit run app.py
```

Open the localhost URL printed by Streamlit. The sidebar shows local model names, document counts, chunk counts, and controls for showing context, clearing chat, or resetting the index.

## CLI Smoke Check

```powershell
python -m wiki_rag.ask "Who was Albert Einstein and what is he known for?" --show-context
```

## Indexed Entities

People:

Albert Einstein, Marie Curie, Leonardo da Vinci, William Shakespeare, Ada Lovelace, Nikola Tesla, Lionel Messi, Cristiano Ronaldo, Taylor Swift, Frida Kahlo, Isaac Newton, Charles Darwin, Nelson Mandela, Mahatma Gandhi, Cleopatra, Ludwig van Beethoven, Wolfgang Amadeus Mozart, Martin Luther King Jr., Pablo Picasso, Oprah Winfrey, Aristotle, Galileo Galilei, Jane Austen, Amelia Earhart, Michael Jackson, Queen Victoria, Abraham Lincoln, Walt Disney, Steve Jobs, Mother Teresa.

Places:

Eiffel Tower, Great Wall of China, Taj Mahal, Grand Canyon, Machu Picchu, Colosseum, Hagia Sophia, Statue of Liberty, Pyramids of Giza, Mount Everest, Louvre, Acropolis of Athens, Stonehenge, Burj Khalifa, Angkor Wat, Petra, Sydney Opera House, Yellowstone National Park, Vatican City, Niagara Falls, Cappadocia, Ephesus, Topkapi Palace, Sultan Ahmed Mosque, Tower of London, Sagrada Familia, Christ the Redeemer, Golden Gate Bridge, Alhambra, Mount Fuji.

## Supported Question Bank

The assistant is designed for questions that can be answered from the indexed Wikipedia pages. You can ask the same patterns about any indexed person or place.

Person question templates:

- Who was `<person>` and what are they known for?
- What did `<person>` discover, create, write, or accomplish?
- Why is `<person>` famous?
- When and where was `<person>` born?
- Compare `<person>` and `<person>`.

Place question templates:

- Where is `<place>` located?
- What is `<place>`?
- Why is `<place>` important or famous?
- What was `<place>` used for?
- Compare `<place>` and `<place>`.

Location and association templates:

- Which famous place is located in Turkey?
- Which famous places are located in Istanbul?
- Which famous place is located in France?
- Which famous place is located in India?
- Which famous place is located in China?
- Which famous place is located in the United States?
- Which person is associated with electricity?
- Which person is associated with radioactivity?
- Which person is associated with relativity?
- Which person is associated with literature?
- Which person is associated with aviation?

Required people examples:

- Who was Albert Einstein and what is he known for?
- What did Marie Curie discover?
- Why is Nikola Tesla famous?
- Compare Lionel Messi and Cristiano Ronaldo.
- What is Frida Kahlo known for?
- Who was Ada Lovelace?
- What is William Shakespeare known for?
- Why is Leonardo da Vinci famous?
- What did Isaac Newton contribute to science?
- What is Jane Austen known for?

Required places examples:

- Where is the Eiffel Tower located?
- Why is the Great Wall of China important?
- What is Machu Picchu?
- What was the Colosseum used for?
- Where is Mount Everest?
- Where is Hagia Sophia located?
- What is Cappadocia known for?
- Where is Ephesus located?
- What is Topkapi Palace?
- Where is Sultan Ahmed Mosque located?

Mixed and comparison examples:

- Which famous place is located in Turkey?
- Which person is associated with electricity?
- Compare Albert Einstein and Nikola Tesla.
- Compare the Eiffel Tower and the Statue of Liberty.
- Compare Hagia Sophia and the Colosseum.
- Compare Cappadocia and Machu Picchu.
- Compare Taylor Swift and Michael Jackson.
- Compare Ada Lovelace and Steve Jobs.

Failure cases:

- Who is the president of Mars?
- Tell me about a random unknown person John Doe.
- Which indexed place is located on the Moon?
- What award did an unknown person named Jane Q. Public win?

## Architecture

1. `wiki_rag.wiki_client` fetches plain-text Wikipedia extracts.
2. `wiki_rag.chunking` splits documents into about 220-word chunks with 45-word overlap.
3. `wiki_rag.storage` saves raw documents and chunks in SQLite.
4. `wiki_rag.ollama_client` calls Ollama's local `/api/embed` and `/api/generate` endpoints.
5. `wiki_rag.vector_store` stores and queries embeddings in one local Chroma collection.
6. `wiki_rag.routing` classifies queries as `person`, `place`, or `both`.
7. `wiki_rag.hints` boosts retrieval for broad location and association questions.
8. `wiki_rag.rag` builds grounded prompts and generates answers from retrieved context.

## Configuration

Environment variables:

- `OLLAMA_BASE_URL`, default `http://localhost:11434`
- `OLLAMA_EMBED_MODEL`, default `nomic-embed-text`
- `OLLAMA_GENERATION_MODEL`, default `llama3.2:3b`
- `WIKI_RAG_DATA_DIR`, default `data`
- `WIKI_RAG_CHUNK_WORDS`, default `220`
- `WIKI_RAG_CHUNK_OVERLAP`, default `45`
- `WIKI_RAG_RETRIEVE_K`, default `8`

## Tests

```powershell
pytest
```

The tests mock Ollama calls and do not require a live local model.

## Troubleshooting

- `Could not connect to Ollama`: start Ollama and confirm `http://localhost:11434` is reachable.
- Model not found: run `ollama pull llama3.2:3b` and `ollama pull nomic-embed-text`.
- Empty app results: run `python -m wiki_rag.ingest --reset` before asking questions.
- Ingestion fails during Wikipedia fetch: check internet connectivity, then rerun ingestion.

## Demo Video

https://www.loom.com/share/a6b7cbca18b94414bf2049a9442398f6

## Author

Doruk Ilhan 820220323 GitHub: https://github.com/dorukilhann/local-wikipedia-rag-assistant
