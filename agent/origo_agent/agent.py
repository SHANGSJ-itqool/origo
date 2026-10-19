"""Origo agent: the task-planning loop.

Local-first LLM + skills (tools). High-risk tool calls are confirmed and
audited. Returns the final natural-language answer. Backend failures are
turned into actionable guidance instead of crashing.
"""
from __future__ import annotations

import json
from typing import Any, Callable

from .config import Config
from .llm.openai_compatible import LLMError
from .llm.router import LLMRouter
from .memory import Memory
from .safety import ConfirmationUnavailableError, Safety
from .skills.base import Skill

SYSTEM_PROMPT = (
    "You are Origo (元启), the agent core of an AI-native minimal operating "
    "system. Your job is to help the user accomplish real tasks using the "
    "provided tools. Prefer the simplest path, check facts with tools, and "
    "perform multi-step work yourself. The system will ask the user to "
    "confirm high-risk actions. If a task cannot be done with the available "
    "tools, say so plainly and name the missing capability. Keep answers "
    "concise and actionable."
)


def _backend_guidance(cfg: Config, exc: Exception) -> str:
    return (
        "我还没有连上可用的模型后端（本地“大脑”），所以暂时无法思考或执行任务。\n"
        f"诊断信息：{exc}\n\n"
        "可以按下面任一方式处理：\n"
        "1) 安装并启动本地模型（推荐，离线、隐私）：\n"
        "     curl -fsSL https://ollama.com/install.sh | sh\n"
        f"     ollama pull {cfg.model}\n"
        "   （Origo 完整版镜像已内置；精简版可在桌面运行“Origo 本地模型向导”）\n"
        "2) 改用兼容 OpenAI 的云端：设置 ORIGO_CLOUD_BASE_URL、ORIGO_CLOUD_API_KEY、"
        "ORIGO_CLOUD_MODEL，并用 --allow-cloud 启动。\n"
        "3) 若你确认本地服务已启动，请检查它是否在监听（默认 http://localhost:11434），"
        "以及模型名是否与配置一致。"
    )


class Agent:
    def __init__(
        self,
        cfg: Config,
        skills: list[Skill],
        on_event: Callable[[str, str], None] | None = None,
    ):
        self.cfg = cfg
        self.skills = {s.name: s for s in skills}
        self.router = LLMRouter(cfg)
        self.memory = Memory(cfg.data_dir, enabled=True)
        self.safety = Safety(
            cfg.data_dir,
            require_confirmation=cfg.require_confirmation,
            auto_approve=cfg.auto_approve,
        )
        self.on_event = on_event or (lambda kind, text: None)

    def _emit(self, kind: str, text: str) -> None:
        self.on_event(kind, text)

    def run(self, user_input: str) -> str:
        self.memory.append("user", user_input)
        messages: list[dict[str, Any]] = [{"role": "system", "content": SYSTEM_PROMPT}]
        messages.extend(self.memory.recent())
        tools = [s.tool_spec() for s in self.skills.values()]

        try:
            for _ in range(self.cfg.max_steps):
                message, label = self.router.chat(messages, tools=tools)
                self._emit("backend", label)
                tool_calls = message.get("tool_calls") or []

                if not tool_calls:
                    answer = message.get("content", "") or ""
                    self.memory.append("assistant", answer)
                    return answer

                # Record the assistant message (tool calls) then execute each.
                messages.append(message)
                for call in tool_calls:
                    fn = call.get("function", {})
                    name = fn.get("name", "")
                    raw_args = fn.get("arguments", "{}")
                    try:
                        args = json.loads(raw_args) if raw_args else {}
                    except json.JSONDecodeError:
                        args = {}

                    skill = self.skills.get(name)
                    if skill is None:
                        result_text = f"unknown tool: {name}"
                        self._emit("error", result_text)
                    else:
                        try:
                            if self.safety.needs_confirmation(skill, args):
                                if not self.safety.confirm(skill, args):
                                    result_text = "User declined this action."
                                    self._emit("declined", f"{name} declined")
                                else:
                                    result_text = self._execute(skill, args)
                            else:
                                result_text = self._execute(skill, args)
                        except ConfirmationUnavailableError as exc:
                            result_text = f"ERROR: {exc}"
                            self._emit("error", "confirmation unavailable")

                    self.safety.audit("tool", name, args, result_text)
                    messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": call.get("id", ""),
                            "name": name,
                            "content": result_text,
                        }
                    )
        except LLMError as exc:
            self._emit("error", "no model backend")
            return _backend_guidance(self.cfg, exc)

        fallback = "Reached the step limit before finishing. Want me to continue?"
        self.memory.append("assistant", fallback)
        return fallback

    def _execute(self, skill: Skill, args: dict) -> str:
        self._emit("tool", f"{skill.name} {json.dumps(args, ensure_ascii=False)[:160]}")
        result = skill.run(**args)
        return result.as_tool_message()

    def reset_memory(self) -> None:
        self.memory.clear()

    def close(self) -> None:
        self.memory.close()
