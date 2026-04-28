from __future__ import annotations

import streamlit as st

from wiki_rag.config import get_config
from wiki_rag.rag import RAGAssistant
from wiki_rag.storage import SQLiteStore
from wiki_rag.vector_store import VectorStore


st.set_page_config(page_title="Local Wikipedia RAG", page_icon=":mag:", layout="wide")


@st.cache_resource(show_spinner=False)
def get_assistant() -> RAGAssistant:
    return RAGAssistant()


def reset_local_index() -> None:
    config = get_config()
    store = SQLiteStore(config.sqlite_path)
    store.initialize()
    store.reset()
    vector_store = VectorStore(config.chroma_path, config.collection_name)
    vector_store.reset()
    get_assistant.clear()


config = get_config()
store = SQLiteStore(config.sqlite_path)
store.initialize()

if "messages" not in st.session_state:
    st.session_state.messages = []

st.title("Local Wikipedia RAG")

with st.sidebar:
    st.subheader("Local setup")
    st.caption(f"Generation: `{config.generation_model}`")
    st.caption(f"Embeddings: `{config.embed_model}`")
    st.caption(f"Documents: `{store.count_documents()}`")
    st.caption(f"Chunks: `{store.count_chunks()}`")
    show_context = st.toggle("Show retrieved context", value=True)
    if st.button("Clear chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    if st.button("Reset local index", use_container_width=True):
        reset_local_index()
        st.session_state.messages = []
        st.rerun()

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if show_context and message.get("context"):
            with st.expander("Retrieved context"):
                for item in message["context"]:
                    st.markdown(
                        f"**{item['title']}** - {item['entity_type']} - chunk {item['chunk_index']}"
                    )
                    st.caption(item["source_url"])
                    st.write(item["text"])

query = st.chat_input("Ask about the indexed people and places")
if query:
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.markdown(query)

    with st.chat_message("assistant"):
        try:
            with st.spinner("Retrieving and generating locally..."):
                result = get_assistant().answer(query)
            st.markdown(result.answer)
            context = [
                {
                    "title": chunk.title,
                    "entity_type": chunk.entity_type,
                    "chunk_index": chunk.chunk_index,
                    "source_url": chunk.source_url,
                    "text": chunk.text,
                }
                for chunk in result.retrieved_chunks
            ]
            if show_context and context:
                with st.expander("Retrieved context"):
                    for item in context:
                        st.markdown(
                            f"**{item['title']}** - {item['entity_type']} - chunk {item['chunk_index']}"
                        )
                        st.caption(item["source_url"])
                        st.write(item["text"])
            st.session_state.messages.append(
                {"role": "assistant", "content": result.answer, "context": context}
            )
        except Exception as exc:
            message = f"Local RAG error: {exc}"
            st.error(message)
            st.session_state.messages.append(
                {"role": "assistant", "content": message, "context": []}
            )
