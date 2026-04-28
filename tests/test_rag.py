from wiki_rag.rag import build_context, build_prompt
from wiki_rag.routing import QueryRoute
from wiki_rag.storage import StoredChunk
from wiki_rag.vector_store import RetrievedChunk


def sample_chunk() -> RetrievedChunk:
    return RetrievedChunk(
        chunk_id="einstein-0000",
        text="Albert Einstein was a theoretical physicist known for relativity.",
        title="Albert Einstein",
        entity_type="person",
        source_url="https://en.wikipedia.org/wiki/Albert_Einstein",
        chunk_index=0,
        distance=0.1,
    )


def test_build_context_includes_source_metadata():
    context = build_context([sample_chunk()])

    assert "Albert Einstein" in context
    assert "Source title:" in context
    assert "Source URL:" in context
    assert "relativity" in context


def test_prompt_requires_unknown_answer_when_context_is_missing():
    prompt = build_prompt("Who is the president of Mars?", [])

    assert "I don't know" in prompt
    assert "Do not use outside knowledge" in prompt
    assert "No relevant context was retrieved" in prompt


def test_prompt_asks_for_page_title_citations_only():
    prompt = build_prompt("Where is the Eiffel Tower located?", [sample_chunk()])

    assert "use only the Wikipedia page title" in prompt
    assert "Do not cite chunk numbers" in prompt


def test_prompt_guides_comparison_questions():
    prompt = build_prompt("Compare Taylor Swift and Michael Jackson.", [sample_chunk()])

    assert "For comparison questions" in prompt
    assert "compare the named source titles" in prompt


def test_priority_context_prepends_named_entity_chunks():
    from wiki_rag.rag import RAGAssistant

    class FakeStore:
        def initialize(self):
            pass

        def first_chunks_for_title(self, title, limit=2):
            if title != "Eiffel Tower":
                return []
            return [
                StoredChunk(
                    chunk_id="eiffel-0000",
                    title="Eiffel Tower",
                    entity_type="place",
                    source_url="https://en.wikipedia.org/wiki/Eiffel_Tower",
                    chunk_index=0,
                    text="The Eiffel Tower is on the Champ de Mars in Paris, France.",
                    word_count=13,
                )
            ]

    assistant = RAGAssistant(
        ollama_client=object(),
        vector_store=object(),
        sqlite_store=FakeStore(),
    )
    route = QueryRoute("place", "matched known place name", (), ("Eiffel Tower",))

    chunks = assistant._prepend_priority_context(route, "Where is the Eiffel Tower?", [])

    assert chunks[0].title == "Eiffel Tower"
    assert "Paris, France" in chunks[0].text


def test_priority_context_prepends_location_hint_chunks():
    from wiki_rag.rag import RAGAssistant

    class FakeStore:
        def initialize(self):
            pass

        def first_chunks_for_title(self, title, limit=2):
            if title != "Hagia Sophia":
                return []
            return [
                StoredChunk(
                    chunk_id="hagia-0000",
                    title="Hagia Sophia",
                    entity_type="place",
                    source_url="https://en.wikipedia.org/wiki/Hagia_Sophia",
                    chunk_index=0,
                    text="Hagia Sophia is a major cultural site in Istanbul, Turkey.",
                    word_count=10,
                )
            ]

    assistant = RAGAssistant(
        ollama_client=object(),
        vector_store=object(),
        sqlite_store=FakeStore(),
    )
    route = QueryRoute("place", "matched place keywords", (), ())

    chunks = assistant._prepend_priority_context(
        route, "Which famous place is located in Turkey?", []
    )

    assert chunks[0].title == "Hagia Sophia"
    assert "Turkey" in chunks[0].text
