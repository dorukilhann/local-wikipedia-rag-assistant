"""Direct local HTTP client for Ollama generation and embeddings."""

from __future__ import annotations

from typing import Any

import requests


class OllamaError(RuntimeError):
    pass


class OllamaClient:
    def __init__(self, base_url: str, timeout: int = 120):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def _post(self, path: str, payload: dict[str, Any], timeout: int | None = None) -> dict[str, Any]:
        url = f"{self.base_url}{path}"
        try:
            response = requests.post(url, json=payload, timeout=timeout or self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.ConnectionError as exc:
            raise OllamaError(
                "Could not connect to Ollama. Start Ollama locally and pull the required models."
            ) from exc
        except requests.Timeout as exc:
            raise OllamaError(f"Ollama request timed out at {url}") from exc
        except requests.HTTPError as exc:
            detail = getattr(exc.response, "text", "") if exc.response is not None else ""
            raise OllamaError(f"Ollama returned an HTTP error: {detail}") from exc
        except ValueError as exc:
            raise OllamaError("Ollama returned invalid JSON") from exc

    def embed_texts(self, texts: list[str], model: str) -> list[list[float]]:
        if not texts:
            return []
        payload = {"model": model, "input": texts}
        data = self._post("/api/embed", payload)
        embeddings = data.get("embeddings")
        if not isinstance(embeddings, list) or len(embeddings) != len(texts):
            raise OllamaError("Ollama embedding response did not match the input batch")
        return embeddings

    def generate(self, prompt: str, model: str, timeout: int | None = None) -> str:
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.1, "top_p": 0.9},
        }
        data = self._post("/api/generate", payload, timeout=timeout)
        response = data.get("response")
        if not isinstance(response, str):
            raise OllamaError("Ollama generation response did not contain text")
        return response.strip()
