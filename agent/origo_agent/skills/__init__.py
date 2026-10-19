"""Origo skills: capabilities the agent can call.

Each skill is a typed tool with a risk level. High-risk skills are gated by
the safety policy (human confirmation).
"""
from .base import Skill, SkillResult, Risk
from .terminal import TerminalSkill
from .files import FileReadSkill, FileWriteSkill
from .browser import BrowserSkill
from .settings import SettingsSkill
from .apps import LaunchAppSkill


def default_skills() -> list[Skill]:
    return [
        TerminalSkill(),
        FileReadSkill(),
        FileWriteSkill(),
        BrowserSkill(),
        SettingsSkill(),
        LaunchAppSkill(),
    ]

__all__ = ["Skill", "SkillResult", "Risk", "default_skills"]
