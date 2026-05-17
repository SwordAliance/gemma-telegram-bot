"""Этот модуль превращает длинный диалог в краткое резюме."""
from __future__ import annotations

from dataclasses import dataclass

from db import MemoryDB
from llm import LLMClient


@dataclass(frozen=True)
class MemoryBundle:
    summary: str
    recent_messages: list[dict[str, str]]


class MemoryManager:
    def __init__(self, db: MemoryDB, llm: LLMClient, summary_trigger_messages: int, max_history_messages: int) -> None:
        self.db = db
        self.llm = llm
        self.summary_trigger_messages = summary_trigger_messages
        self.max_history_messages = max_history_messages

    def build_memory_bundle(self, chat_id: int) -> MemoryBundle:
        summary = self.db.get_summary(chat_id)
        recent = self.db.get_recent_messages(chat_id, self.max_history_messages)
        recent_messages = [{"role": row.role, "content": row.content} for row in recent]
        return MemoryBundle(summary=summary, recent_messages=recent_messages)

    async def maybe_summarize(self, chat_id: int) -> None:
        count = self.db.count_messages(chat_id)
        if count < self.summary_trigger_messages:
            return

        summary = self.db.get_summary(chat_id)
        recent = self.db.get_recent_messages(chat_id, self.max_history_messages)

        transcript = "\n".join(f"{row.role.upper()}: {row.content}" for row in recent)
        prompt = [
            {
                "role": "system",
                "content": (
                    "Сожми историю диалога в краткое, но полезное резюме. "
                    "Сохрани факты о пользователе, предпочтения, задачи и незавершенные вопросы. "
                    "Не добавляй вымышленных деталей."
                ),
            },
            {
                "role": "user",
                "content": f"Текущее резюме:\n{summary}\n\nПоследние сообщения:\n{transcript}",
            },
        ]

        new_summary = await self.llm.generate_text(prompt, temperature=0.2)
        self.db.upsert_summary(chat_id, new_summary.strip())
        self.db.trim_messages_keep_last(chat_id, self.max_history_messages)
