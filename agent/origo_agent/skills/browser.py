"""Browser skill: open a URL or fetch a page."""
from __future__ import annotations

import shutil
import subprocess
import urllib.request

from .base import Risk, Skill, SkillResult


class BrowserSkill(Skill):
    name = "browser"
    description = (
        "Open a URL in the default browser, or fetch a page's text. Pass "
        "action='open' (default, opens GUI) or action='fetch' (returns text)."
    )
    risk = Risk.MEDIUM
    parameters = {
        "type": "object",
        "properties": {
            "url": {"type": "string", "description": "Full URL (https://...)"},
            "action": {"type": "string", "enum": ["open", "fetch"], "default": "open"},
        },
        "required": ["url"],
    }

    def run(self, url: str = "", action: str = "open", **_):
        if not url:
            return SkillResult(False, "missing url")
        try:
            if action == "fetch":
                with urllib.request.urlopen(url, timeout=20) as resp:  # noqa: S310
                    raw = resp.read(2_000_000).decode("utf-8", errors="replace")
                return SkillResult(True, raw[:6000])
            opener = shutil.which("xdg-open")
            if not opener:
                return SkillResult(False, "no default browser (xdg-open)")
            subprocess.Popen(["xdg-open", url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return SkillResult(True, f"opened {url}")
        except Exception as exc:  # noqa: BLE001
            return SkillResult(False, str(exc))
