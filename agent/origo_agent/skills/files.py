"""File skills: read and write files."""
from __future__ import annotations

from pathlib import Path

from .base import Risk, Skill, SkillResult


class FileReadSkill(Skill):
    name = "file_read"
    description = "Read a UTF-8 text file and return its contents (read-only)."
    risk = Risk.LOW
    parameters = {
        "type": "object",
        "properties": {"path": {"type": "string", "description": "Absolute file path"}},
        "required": ["path"],
    }

    def run(self, path: str = "", **_):
        try:
            p = Path(path).expanduser()
            if not p.is_file():
                return SkillResult(False, f"not a file: {path}")
            if p.stat().st_size > 2_000_000:
                return SkillResult(False, "file too large (>2MB)")
            return SkillResult(True, p.read_text(encoding="utf-8", errors="replace")[:6000])
        except Exception as exc:  # noqa: BLE001
            return SkillResult(False, str(exc))


class FileWriteSkill(Skill):
    name = "file_write"
    description = "Create or overwrite a text file with given contents. High risk."
    risk = Risk.HIGH
    parameters = {
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Absolute file path"},
            "contents": {"type": "string", "description": "Full file contents"},
        },
        "required": ["path", "contents"],
    }

    def run(self, path: str = "", contents: str = "", **_):
        try:
            p = Path(path).expanduser()
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(contents, encoding="utf-8")
            return SkillResult(True, f"wrote {len(contents)} bytes to {p}")
        except Exception as exc:  # noqa: BLE001
            return SkillResult(False, str(exc))
