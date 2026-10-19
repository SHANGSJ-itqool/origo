"""Safety policy: risk classification, confirmation gate, audit log."""
from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path

from rich.console import Console

from .skills.base import Risk, Skill


class ConfirmationUnavailableError(RuntimeError):
    """Raised when a high-risk action needs confirmation but there is no
    interactive terminal and the user did not pre-authorize it (--yes)."""


class Safety:
    def __init__(
        self,
        data_dir: Path,
        require_confirmation: bool = True,
        auto_approve: bool = False,
        console: Console | None = None,
    ):
        self.require_confirmation = require_confirmation
        self.auto_approve = auto_approve
        self.console = console or Console()
        self.audit_path = Path(data_dir) / "audit.log"
        self.audit_path.parent.mkdir(parents=True, exist_ok=True)

    def needs_confirmation(self, skill: Skill, args: dict) -> bool:
        return skill.risk == Risk.HIGH and self.require_confirmation

    def confirm(self, skill: Skill, args: dict) -> bool:
        detail = json.dumps(args, ensure_ascii=False)[:200]
        if self.auto_approve:
            self.console.print(
                f"[bold yellow]CONFIRM[/] '{skill.name}' {detail} -> "
                "[green]auto-approved (--yes)[/]"
            )
            return True
        if not sys.stdin.isatty():
            raise ConfirmationUnavailableError(
                f"'{skill.name}' is a high-risk action and needs confirmation, but there is "
                "no interactive terminal. Re-run with --yes to pre-authorize this action, "
                "or run the agent in a terminal where you can answer y/N."
            )
        answer = self.console.input(
            f"[bold yellow]CONFIRM[/] Allow '[bold]{skill.name}[/]' with {detail}? [y/N] "
        ).strip().lower()
        return answer in ("y", "yes")

    def audit(self, kind: str, name: str, args: dict, result: str) -> None:
        entry = {
            "ts": datetime.now().isoformat(timespec="seconds"),
            "kind": kind,
            "skill": name,
            "args": args,
            "result": (result or "")[:500],
        }
        try:
            with open(self.audit_path, "a", encoding="utf-8") as fh:
                fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
        except OSError:
            print(f"audit write failed: {entry}", file=sys.stderr)
