"""Settings skill: open system settings panels."""
from __future__ import annotations

import shutil
import subprocess

from .base import Risk, Skill, SkillResult

_PANELS = {
    "network": "gnome-control-center network",
    "wifi": "gnome-control-center wifi",
    "bluetooth": "gnome-control-center bluetooth",
    "sound": "gnome-control-center sound",
    "display": "gnome-control-center display",
    "power": "gnome-control-center power",
    "keyboard": "gnome-control-center keyboard",
    "about": "gnome-control-center about",
}


class SettingsSkill(Skill):
    name = "settings"
    description = (
        "Open a system settings panel: network, wifi, bluetooth, sound, "
        "display, power, keyboard, about."
    )
    risk = Risk.LOW
    parameters = {
        "type": "object",
        "properties": {"panel": {"type": "string", "description": "Panel name"}},
        "required": ["panel"],
    }

    def run(self, panel: str = "", **_):
        cmd = _PANELS.get(panel.strip().lower())
        if cmd is None:
            return SkillResult(False, f"unknown panel '{panel}'")
        if shutil.which(cmd.split()[0]) is None:
            return SkillResult(False, f"{cmd.split()[0]} not available")
        try:
            subprocess.Popen(cmd.split(), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return SkillResult(True, f"opened {panel} settings")
        except Exception as exc:  # noqa: BLE001
            return SkillResult(False, str(exc))
