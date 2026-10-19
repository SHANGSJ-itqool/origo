"""Persistent memory: conversation history in SQLite.

Local by default; the user can inspect or clear it.
"""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any


class Memory:
    def __init__(self, data_dir: Path, enabled: bool = True, max_messages: int = 40):
        self.enabled = enabled
        self.max_messages = max_messages
        self.db_path = Path(data_dir) / "memory.db"
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._con = sqlite3.connect(self.db_path)
        self._con.execute(
            "CREATE TABLE IF NOT EXISTS messages ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT, role TEXT, content TEXT, ts TEXT DEFAULT (datetime('now')))"
        )
        self._con.commit()

    def append(self, role: str, content: Any) -> None:
        if not self.enabled:
            return
        payload = content if isinstance(content, str) else json.dumps(content, ensure_ascii=False)
        self._con.execute("INSERT INTO messages(role, content) VALUES (?, ?)", (role, payload))
        self._con.commit()

    def recent(self) -> list[dict[str, str]]:
        if not self.enabled:
            return []
        rows = self._con.execute(
            "SELECT role, content FROM messages ORDER BY id DESC LIMIT ?", (self.max_messages,)
        ).fetchall()
        return [{"role": r, "content": c} for r, c in reversed(rows)]

    def clear(self) -> None:
        self._con.execute("DELETE FROM messages")
        self._con.commit()

    def close(self) -> None:
        self._con.close()
