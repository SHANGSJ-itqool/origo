"""Minimal OpenAI-compatible chat client.

Works with Ollama (http://localhost:11434/v1), llama.cpp's server, and any
OpenAI-compatible cloud endpoint. Only depends on `requests`.
"""
from __future__ import annotations

from typing import Any

import requests


class LLMError(RuntimeError):
    pass


class OpenAICompatibleClient:
    def __init__(self, base_url: str, model: str, api_key: str = "", timeout: int = 120):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout
        self.headers = {"Content-Type": "application/json"}
        if api_key:
            self.headers["Authorization"] = f"Bearer {api_key}"

    def is_available(self) -> bool:
        try:
            r = requests.get(f"{self.base_url}/models", headers=self.headers, timeout=5)
            return r.status_code == 200
        except requests.RequestException:
            return False

    def chat(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
        temperature: float = 0.3,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
        }
        if tools:
            payload["tools"] = tools

        try:
            r = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=self.timeout,
            )
            r.raise_for_status()
        except requests.RequestException as exc:
            raise LLMError(f"LLM request failed ({self.base_url}, model={self.model}): {exc}") from exc

        data = r.json()
        try:
            return data["choices"][0]["message"]
        except (KeyError, IndexError) as exc:
            raise LLMError(f"Unexpected LLM response: {data}") from exc
