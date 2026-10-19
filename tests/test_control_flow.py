"""Control-flow tests for the Origo agent using a fake OpenAI-compatible backend.

These verify the control flow (tool-call loop, safety gate, no-backend
guidance, settings detection, model alignment, CLI flags) WITHOUT any real
model or GPU: the "backend" is a scripted HTTP server.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

# Make the agent package importable.
AGENT_SRC = Path(__file__).resolve().parents[1] / "agent"
sys.path.insert(0, str(AGENT_SRC))

from origo_agent.agent import Agent  # noqa: E402
from origo_agent.config import Config  # noqa: E402
from origo_agent.skills import default_skills  # noqa: E402
from origo_agent.skills.settings import SettingsSkill  # noqa: E402


class FakeHandler(BaseHTTPRequestHandler):
    script: list = []  # scripted responses
    calls: list = []   # captured requests

    def log_message(self, *args):
        pass

    def _send(self, code, obj):
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path.endswith("/models"):
            self._send(200, {"object": "list", "data": []})
        else:
            self._send(404, {"error": "not found"})

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        data = json.loads(self.rfile.read(length) or b"{}")
        self.calls.append(data)
        if self.path.endswith("/chat/completions"):
            kind, payload = self.script.pop(0) if self.script else ("final", {"content": "?"})
            if kind == "tool":
                message = {
                    "role": "assistant",
                    "content": "",
                    "tool_calls": [
                        {
                            "id": "call_1",
                            "type": "function",
                            "function": {
                                "name": payload["name"],
                                "arguments": json.dumps(payload["arguments"]),
                            },
                        }
                    ],
                }
            else:
                message = {"role": "assistant", "content": payload["content"]}
            self._send(200, {"choices": [{"message": message}]})
        else:
            self._send(404, {"error": "not found"})


def start_server(script):
    FakeHandler.script = list(script)
    FakeHandler.calls = []
    server = HTTPServer(("127.0.0.1", 0), FakeHandler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server


def make_cfg(base_url, data_dir, **overrides):
    cfg = Config()
    cfg.local_base_url = base_url
    cfg.data_dir = Path(data_dir)
    cfg.require_confirmation = True
    cfg.auto_approve = False
    for k, v in overrides.items():
        setattr(cfg, k, v)
    return cfg


class TestControlFlow(unittest.TestCase):
    def test_01_no_backend_guidance(self):
        with tempfile.TemporaryDirectory() as d:
            cfg = make_cfg("http://127.0.0.1:9/v1", d)  # nothing listening
            agent = Agent(cfg, default_skills())
            out = agent.run("你好")
            self.assertIn("模型后端", out)
            self.assertIn("ollama", out.lower())
            agent.close()

    def test_02_tool_call_loop_low_risk(self):
        with tempfile.TemporaryDirectory() as d:
            sample = Path(d) / "note.txt"
            sample.write_text("hello-origo", encoding="utf-8")
            server = start_server([
                ("tool", {"name": "file_read", "arguments": {"path": str(sample)}}),
                ("final", {"content": "读到了: hello-origo"}),
            ])
            cfg = make_cfg(f"http://127.0.0.1:{server.server_address[1]}/v1", d)
            agent = Agent(cfg, default_skills())
            out = agent.run("读一下那个文件")
            self.assertIn("hello-origo", out)
            self.assertEqual(len(FakeHandler.calls), 2)
            server.shutdown()
            server.server_close()
            agent.close()

    def test_03_high_risk_non_tty_explicit_error(self):
        with tempfile.TemporaryDirectory() as d:
            server = start_server([
                ("tool", {"name": "terminal", "arguments": {"command": "echo hi"}}),
                ("final", {"content": "BLOCKED"}),
            ])
            cfg = make_cfg(f"http://127.0.0.1:{server.server_address[1]}/v1", d)
            agent = Agent(cfg, default_skills())
            out = agent.run("执行 echo hi")
            self.assertEqual(out, "BLOCKED")
            # The explicit error was fed back to the model (not a silent decline).
            second = FakeHandler.calls[1]
            blob = json.dumps(second, ensure_ascii=False)
            self.assertIn("no interactive terminal", blob)
            self.assertNotIn("User declined", blob)
            server.shutdown()
            server.server_close()
            agent.close()

    def test_04_high_risk_auto_approve(self):
        with tempfile.TemporaryDirectory() as d:
            server = start_server([
                ("tool", {"name": "terminal", "arguments": {"command": "echo hello-origo"}}),
                ("final", {"content": "命令已执行"}),
            ])
            cfg = make_cfg(
                f"http://127.0.0.1:{server.server_address[1]}/v1", d, auto_approve=True
            )
            agent = Agent(cfg, default_skills())
            out = agent.run("执行 echo")
            self.assertIn("命令已执行", out)
            # The command truly ran and its output was sent back to the model.
            self.assertIn("hello-origo", json.dumps(FakeHandler.calls))
            server.shutdown()
            server.server_close()
            agent.close()

    def test_05_settings_uses_candidates(self):
        skill = SettingsSkill()
        result = skill.run(panel="display")
        text = result.output
        # It either opens a real tool or clearly names the candidates; it must
        # never be the hardcoded "gnome-control-center not available".
        self.assertIn("display", text)
        self.assertTrue(("via" in text) or ("tried" in text))
        self.assertNotEqual(text, "gnome-control-center not available")
        unknown = skill.run(panel="nope")
        self.assertFalse(unknown.ok)
        self.assertIn("unknown panel", unknown.output)

    def test_06_model_default_alignment(self):
        self.assertEqual(Config().model, "qwen3:1.7b")

    def test_07_cli_flags(self):
        env = {**os.environ, "PYTHONPATH": str(AGENT_SRC)}
        help_out = subprocess.run(
            [sys.executable, "-m", "origo_agent", "--help"],
            capture_output=True, text=True, env=env,
        ).stdout
        self.assertIn("--yes", help_out)
        self.assertIn("--model", help_out)
        version = subprocess.run(
            [sys.executable, "-m", "origo_agent", "--version"],
            capture_output=True, text=True, env=env,
        ).stdout
        self.assertIn("0.1.0", version)


if __name__ == "__main__":
    unittest.main(verbosity=2)
