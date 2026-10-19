"""Configuration for Origo agent.

Load order (later overrides earlier):
  1. built-in defaults
  2. system config: /etc/origo/config.toml   (laid down by the image)
  3. user config:   ~/.config/origo/config.toml
  4. environment variables
Sensible local-first defaults so the agent works without setup.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

try:  # Python 3.11+
    import tomllib as _toml
except ModuleNotFoundError:  # pragma: no cover - fallback for 3.10
    _toml = None

SYSTEM_CONFIG = Path("/etc/origo/config.toml")


def _config_dir() -> Path:
    base = os.environ.get("XDG_CONFIG_HOME")
    return Path(base) / "origo" if base else Path.home() / ".config" / "origo"


@dataclass
class Config:
    model: str = "qwen3:1.7b"
    local_base_url: str = "http://localhost:11434/v1"
    cloud_base_url: str = ""
    cloud_api_key: str = ""
    cloud_model: str = ""
    allow_cloud: bool = False
    require_confirmation: bool = True
    auto_approve: bool = False
    max_steps: int = 10
    data_dir: Path = field(default_factory=lambda: Path.home() / ".local" / "share" / "origo")

    @staticmethod
    def load() -> "Config":
        cfg = Config()

        def apply_toml(path: Path) -> None:
            if path.exists() and _toml is not None:
                with open(path, "rb") as fh:
                    data = _toml.load(fh)
                for k, v in data.items():
                    if hasattr(cfg, k):
                        setattr(cfg, k, v)

        # 2. system config, then 3. user config.
        apply_toml(SYSTEM_CONFIG)
        apply_toml(_config_dir() / "config.toml")

        # 4. environment variables.
        env_map = {
            "model": "ORIGO_MODEL",
            "local_base_url": "ORIGO_LOCAL_BASE_URL",
            "cloud_base_url": "ORIGO_CLOUD_BASE_URL",
            "cloud_api_key": "ORIGO_CLOUD_API_KEY",
            "cloud_model": "ORIGO_CLOUD_MODEL",
            "max_steps": "ORIGO_MAX_STEPS",
        }
        for attr, env in env_map.items():
            val = os.environ.get(env)
            if val:
                cur = getattr(cfg, attr)
                setattr(cfg, attr, type(cur)(val) if not isinstance(cur, Path) else val)

        cfg.allow_cloud = os.environ.get("ORIGO_ALLOW_CLOUD", "0") == "1"
        if os.environ.get("ORIGO_NO_CONFIRM", "0") == "1":
            cfg.require_confirmation = False
        if os.environ.get("ORIGO_YES", "0") == "1":
            cfg.auto_approve = True
        cfg.data_dir = Path(cfg.data_dir)
        cfg.data_dir.mkdir(parents=True, exist_ok=True)
        return cfg
