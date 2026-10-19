"""Skill base classes."""
from __future__ import annotations

import enum
from dataclasses import dataclass
from typing import Any


class Risk(str, enum.Enum):
    LOW = "low"        # read-only, safe
    MEDIUM = "medium"  # reversible, local side effects
    HIGH = "high"      # destructive / irreversible / outward-facing


@dataclass
class SkillResult:
    ok: bool
    output: str

    def as_tool_message(self) -> str:
        return self.output if self.ok else f"ERROR: {self.output}"


class Skill:
    name: str = "skill"
    description: str = ""
    risk: Risk = Risk.LOW
    parameters: dict[str, Any] = {"type": "object", "properties": {}}

    def tool_spec(self) -> dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }

    def run(self, **kwargs: Any) -> SkillResult:  # pragma: no cover - interface
        raise NotImplementedError
