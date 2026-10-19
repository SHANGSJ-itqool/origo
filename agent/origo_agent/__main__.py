"""Origo agent entry point."""
from __future__ import annotations

import argparse

from . import __version__
from .config import Config
from .ui.tui import TUI


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="origo-agent", description="Origo (元启) AI-native agent"
    )
    parser.add_argument("prompt", nargs="?", help="Run a single prompt and exit")
    parser.add_argument("--model", metavar="NAME", help="Model name (overrides config)")
    parser.add_argument("--allow-cloud", action="store_true", help="Permit cloud routing")
    parser.add_argument(
        "-y",
        "--yes",
        action="store_true",
        help="Pre-authorize high-risk actions (for non-interactive / one-shot use)",
    )
    parser.add_argument(
        "--no-confirm",
        action="store_true",
        help="UNSAFE: globally disable the confirmation gate",
    )
    parser.add_argument("--reset", action="store_true", help="Clear memory and exit")
    parser.add_argument("--version", action="version", version=f"origo-agent {__version__}")
    args = parser.parse_args()

    cfg = Config.load()
    if args.model:
        cfg.model = args.model
    if args.allow_cloud:
        cfg.allow_cloud = True
    if args.yes:
        cfg.auto_approve = True
    if args.no_confirm:
        cfg.require_confirmation = False

    tui = TUI(cfg)
    if args.reset:
        tui.agent.reset_memory()
        print("memory cleared.")
        return
    if args.prompt:
        tui.one(args.prompt)
        tui.agent.close()
    else:
        tui.loop()


if __name__ == "__main__":
    main()
