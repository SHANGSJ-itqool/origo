"""Terminal skill: run a shell command."""
from __future__ import annotations

import subprocess

from .base import Risk, Skill, SkillResult


class TerminalSkill(Skill):
    name = "terminal"
    description = (
        "Run a shell command and return combined stdout/stderr. Use for system "
        "inspection, package operations, automation. Commands are high risk."
    )
    risk = Risk.HIGH
    parameters = {
        "type": "object",
        "properties": {
            "command": {"type": "string", "description": "Shell command to execute"},
            "timeout": {"type": "integer", "description": "Seconds before timeout", "default": 30},
        },
        "required": ["command"],
    }

    def run(self, command: str = "", timeout: int = 30, **_):
        if not command:
            return SkillResult(False, "missing command")
        try:
            proc = subprocess.run(
                ["bash", "-lc", command],
                capture_output=True,
                text=True,
                timeout=min(int(timeout), 180),
            )
            out = (proc.stdout or "") + (proc.stderr or "")
            return SkillResult(proc.returncode == 0, out.strip()[:6000] or "(no output)")
        except subprocess.TimeoutExpired:
            return SkillResult(False, f"timeout after {timeout}s")
        except Exception as exc:  # noqa: BLE001
            return SkillResult(False, str(exc))
