import pytest
import requests

from wiki_rag.ollama_client import OllamaClient, OllamaError


class FakeResponse:
    def __init__(self, payload, status_error=None):
        self.payload = payload
        self.status_error = status_error
        self.text = "error"

    def raise_for_status(self):
        if self.status_error:
            raise self.status_error

    def json(self):
        return self.payload


def test_embed_texts_posts_to_ollama(monkeypatch):
    calls = []

    def fake_post(url, json, timeout):
        calls.append((url, json, timeout))
        return FakeResponse({"embeddings": [[0.1, 0.2], [0.3, 0.4]]})

    monkeypatch.setattr(requests, "post", fake_post)
    client = OllamaClient("http://localhost:11434", timeout=7)

    embeddings = client.embed_texts(["a", "b"], "nomic-embed-text")

    assert embeddings == [[0.1, 0.2], [0.3, 0.4]]
    assert calls[0][0] == "http://localhost:11434/api/embed"
    assert calls[0][1]["model"] == "nomic-embed-text"


def test_generate_posts_non_streaming_request(monkeypatch):
    def fake_post(url, json, timeout):
        assert url == "http://localhost:11434/api/generate"
        assert json["stream"] is False
        return FakeResponse({"response": "Grounded answer"})

    monkeypatch.setattr(requests, "post", fake_post)
    client = OllamaClient("http://localhost:11434")

    assert client.generate("prompt", "llama3.2:3b") == "Grounded answer"


def test_connection_error_has_setup_message(monkeypatch):
    def fake_post(url, json, timeout):
        raise requests.ConnectionError("offline")

    monkeypatch.setattr(requests, "post", fake_post)
    client = OllamaClient("http://localhost:11434")

    with pytest.raises(OllamaError, match="Start Ollama locally"):
        client.generate("prompt", "llama3.2:3b")
