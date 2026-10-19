"""Terminal UI for Origo (rich-based)."""
from __future__ import annotations

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from ..agent import Agent
from ..config import Config
from ..skills import default_skills


HELP = """Commands:
  /help      show this help
  /reset     clear memory
  /cloud ON  allow cloud routing; /cloud OFF  local only (default)
  /exit      quit
Anything else is sent to the agent."""


class TUI:
    def __init__(self, cfg: Config):
        self.console = Console()
        self.cfg = cfg
        self.agent = Agent(cfg, default_skills(), on_event=self._on_event)
        # Share the console so confirmation prompts match the UI styling.
        self.agent.safety.console = self.console

    def _on_event(self, kind: str, text: str) -> None:
        styles = {
            "tool": ("bold yellow", "tool"),
            "backend": ("dim", "backend"),
            "error": ("bold red", "error"),
            "declined": ("bold red", "declined"),
        }
        style, label = styles.get(kind, ("dim", kind))
        if kind == "backend":
            return  # quiet
        self.console.print(Text(f"  [{label}] {text}", style=style))

    def welcome(self) -> None:
        banner = Text()
        banner.append("Origo 元启 ", style="bold blue")
        banner.append("— intent is the interface.\n", style="bold")
        banner.append("Type a goal, or /help. Local-first; cloud off by default.", style="dim")
        self.console.print(Panel(banner, border_style="blue"))

    def one(self, text: str) -> None:
        try:
            with self.console.status("thinking…", spinner="dots"):
                answer = self.agent.run(text)
            self.console.print(Panel(answer, border_style="green", title="Origo"))
        except Exception as exc:  # noqa: BLE001 - last-resort: never crash the UI
            self.console.print(
                Panel(f"[red]{exc}[/]", border_style="red", title="Origo")
            )

    def loop(self) -> None:
        self.welcome()
        while True:
            try:
                text = self.console.input("[bold blue]you>[/] ").strip()
            except (EOFError, KeyboardInterrupt):
                break
            if not text:
                continue
            if text.startswith("/"):
                if self._command(text):
                    break
                continue
            self.one(text)
        self.agent.close()
        self.console.print("[dim]bye.[/]")

    def _command(self, text: str) -> bool:
        parts = text.split()
        cmd = parts[0].lower()
        if cmd in ("/exit", "/quit"):
            return True
        if cmd == "/help":
            self.console.print(HELP)
        elif cmd == "/reset":
            self.agent.reset_memory()
            self.console.print("[yellow]memory cleared.[/]")
        elif cmd == "/cloud":
            state = parts[1].lower() if len(parts) > 1 else ""
            if state == "on":
                self.cfg.allow_cloud = True
                self.console.print("[yellow]cloud enabled (requires cloud config).[/]")
            else:
                self.cfg.allow_cloud = False
                self.console.print("[green]local only.[/]")
        else:
            self.console.print(f"[red]unknown command: {cmd}[/]")
        return False
