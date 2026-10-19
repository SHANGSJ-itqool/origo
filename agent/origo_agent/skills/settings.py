"""Settings skill: open system settings panels.

Each panel lists candidate commands; the first whose binary is on PATH wins.
Xfce / generic tools are preferred (Origo ships Xfce), with GNOME as a
fallback, so this works on whatever desktop is actually installed.
"""
from __future__ import annotations

import shutil
import subprocess

from .base import Risk, Skill, SkillResult

# argv lists, in priority order.
_PANEL_CANDIDATES: dict[str, list[list[str]]] = {
    "network": [
        ["nm-connection-editor"],
        ["xfce4-settings-manager"],
        ["gnome-control-center", "network"],
    ],
    "wifi": [
        ["nm-connection-editor"],
        ["xfce4-settings-manager"],
        ["gnome-control-center", "wifi"],
    ],
    "bluetooth": [
        ["blueman-manager"],
        ["gnome-control-center", "bluetooth"],
    ],
    "sound": [
        ["pavucontrol"],
        ["xfce4-mixer"],
        ["gnome-control-center", "sound"],
    ],
    "display": [
        ["xfce4-display-settings"],
        ["arandr"],
        ["gnome-control-center", "display"],
    ],
    "power": [
        ["xfce4-power-manager-settings"],
        ["xfce4-settings-manager"],
        ["gnome-control-center", "power"],
    ],
    "keyboard": [
        ["xfce4-keyboard-settings"],
        ["gnome-control-center", "keyboard"],
    ],
    "about": [
        ["xfce4-about"],
        ["gnome-control-center", "about"],
    ],
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
        key = panel.strip().lower()
        candidates = _PANEL_CANDIDATES.get(key)
        if candidates is None:
            return SkillResult(False, f"unknown panel '{panel}'")
        for argv in candidates:
            if shutil.which(argv[0]) is not None:
                try:
                    subprocess.Popen(
                        argv, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                    )
                    return SkillResult(True, f"opened {key} settings via {argv[0]}")
                except Exception as exc:  # noqa: BLE001
                    return SkillResult(False, str(exc))
        tried = ", ".join(c[0] for c in candidates)
        return SkillResult(
            False,
            f"no settings tool available for '{key}' (tried: {tried}). Install one, "
            "e.g. 'apt install xfce4-settings pavucontrol'.",
        )
