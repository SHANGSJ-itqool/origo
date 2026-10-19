"""Safety policy: risk classification, confirmation gate, audit log."""
from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path

from .skills.base import Risk, Skill


class Safety:
    def __init__(self, data_dir: Path, require_confirmation: bool = True):
        self.require_confirmation = require_confirmation
        self.audit_path = Path(data_dir) / "audit.log"
        self.audit_path.parent.mkdir(parents=True, exist_ok=True)

    def needs_confirmation(self, skill: Skill, args: dict) -> bool:
        return skill.risk == Risk.HIGH and self.require_confirmation

    def confirm(self, skill: Skill, args: dict) -> bool:
        prompt = f"[CONFIRM] Allow '{skill.name}' with {json.dumps(args, ensure_ascii=False)[:200]}? [y/N] "
        try:
            answer = input(prompt).strip().lower()
        except EOFError:
            return False
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
