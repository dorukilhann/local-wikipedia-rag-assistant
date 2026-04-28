from wiki_rag.chunking import chunk_text


def test_chunk_text_respects_word_limit_for_long_text():
    text = " ".join(f"word{i}" for i in range(520))

    chunks = chunk_text(text, chunk_words=100, overlap_words=20)

    assert len(chunks) > 1
    assert all(chunk.word_count <= 100 for chunk in chunks)
    assert chunks[0].text.split()[-20:] == chunks[1].text.split()[:20]


def test_chunk_text_preserves_short_paragraphs():
    text = "Albert Einstein was a physicist.\n\nMarie Curie studied radioactivity."

    chunks = chunk_text(text, chunk_words=20, overlap_words=5)

    assert len(chunks) == 1
    assert "Albert Einstein" in chunks[0].text
    assert "Marie Curie" in chunks[0].text
