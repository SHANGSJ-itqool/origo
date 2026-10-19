"""Launch application skill."""
from __future__ import annotations

import shutil
import subprocess

from .base import Risk, Skill, SkillResult


class LaunchAppSkill(Skill):
    name = "launch_app"
    description = "Launch an installed application by command name."
    risk = Risk.MEDIUM
    parameters = {
        "type": "object",
        "properties": {"app": {"type": "string", "description": "Executable/command name"}},
        "required": ["app"],
    }

    def run(self, app: str = "", **_):
        app = app.strip()
        if not app:
            return SkillResult(False, "missing app")
        if shutil.which(app) is None:
            return SkillResult(False, f"application not found: {app}")
        try:
            subprocess.Popen(
                ["nohup", app],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )
            return SkillResult(True, f"launched {app}")
        except Exception as exc:  # noqa: BLE001
            return SkillResult(False, str(exc))
