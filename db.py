"""SQLite нужен для устойчивой памяти. Без него бот “забудет” все после перезапуска."""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class MessageRow:
    chat_id: int
    role: str
    content: str
    created_at: str


class MemoryDB:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    chat_id INTEGER NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT (datetime('now'))
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS chat_summaries (
                    chat_id INTEGER PRIMARY KEY,
                    summary TEXT NOT NULL,
                    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
                )
                """
            )
            conn.commit()

    def add_message(self, chat_id: int, role: str, content: str) -> None:
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO messages(chat_id, role, content) VALUES (?, ?, ?)",
                (chat_id, role, content),
            )
            conn.commit()

    def get_recent_messages(self, chat_id: int, limit: int) -> list[MessageRow]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT chat_id, role, content, created_at
                FROM messages
                WHERE chat_id = ?
                ORDER BY id DESC
                LIMIT ?
                """,
                (chat_id, limit),
            ).fetchall()
        return [
            MessageRow(
                chat_id=row["chat_id"],
                role=row["role"],
                content=row["content"],
                created_at=row["created_at"],
            )
            for row in reversed(rows)
        ]

    def count_messages(self, chat_id: int) -> int:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT COUNT(*) AS cnt FROM messages WHERE chat_id = ?",
                (chat_id,),
            ).fetchone()
        return int(row["cnt"]) if row else 0

    def get_summary(self, chat_id: int) -> str:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT summary FROM chat_summaries WHERE chat_id = ?",
                (chat_id,),
            ).fetchone()
        return str(row["summary"]) if row else ""

    def upsert_summary(self, chat_id: int, summary: str) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO chat_summaries(chat_id, summary, updated_at)
                VALUES (?, ?, datetime('now'))
                ON CONFLICT(chat_id) DO UPDATE SET
                    summary = excluded.summary,
                    updated_at = datetime('now')
                """,
                (chat_id, summary),
            )
            conn.commit()

    def trim_messages_keep_last(self, chat_id: int, keep_last: int) -> None:
        with self._connect() as conn:
            ids = conn.execute(
                """
                SELECT id FROM messages
                WHERE chat_id = ?
                ORDER BY id DESC
                LIMIT -1 OFFSET ?
                """,
                (chat_id, keep_last),
            ).fetchall()
            if not ids:
                return
            to_delete = [row["id"] for row in ids]
            conn.executemany(
                "DELETE FROM messages WHERE id = ?",
                [(msg_id,) for msg_id in to_delete],
            )
            conn.commit()
