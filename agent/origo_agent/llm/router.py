"""Local-to-cloud routing for the LLM.

Local is always preferred (privacy, latency, offline). Cloud is only used
when explicitly enabled and the local backend is unavailable or the task
requires it.
"""
from __future__ import annotations

from typing import Any

from ..config import Config
from .openai_compatible import OpenAICompatibleClient


class LLMRouter:
    def __init__(self, cfg: Config):
        self.cfg = cfg
        self.local = OpenAICompatibleClient(cfg.local_base_url, cfg.model)
        self.cloud: OpenAICompatibleClient | None = None
        if cfg.allow_cloud and cfg.cloud_base_url and cfg.cloud_model:
            self.cloud = OpenAICompatibleClient(
                cfg.cloud_base_url, cfg.cloud_model, api_key=cfg.cloud_api_key
            )

    def select(self, prefer_cloud: bool = False) -> tuple[OpenAICompatibleClient, str]:
        """Return (client, label)."""
        if prefer_cloud and self.cloud is not None:
            return self.cloud, "cloud"
        if self.local.is_available():
            return self.local, "local"
        if self.cloud is not None:
            return self.cloud, "cloud"
        return self.local, "local"  # will raise on chat with a clear error

    def chat(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
        prefer_cloud: bool = False,
    ) -> tuple[dict[str, Any], str]:
        client, label = self.select(prefer_cloud=prefer_cloud)
        return client.chat(messages, tools=tools), label
