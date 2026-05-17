"""Бот получает вопрос.
Собирает память и документы.
Модель либо отвечает сразу, либо возвращает JSON-инструкцию.
Бот вызывает tool.
Tool-result возвращается в модель.
Модель формирует итог."""

from __future__ import annotations

import json
from dataclasses import dataclass

from db import MemoryDB
from llm import LLMClient
from memory import MemoryManager
from rag import KnowledgeBase
from tools import execute_tool, format_knowledge_results, TOOL_SCHEMA


@dataclass
class AssistantCore:
    db: MemoryDB
    llm: LLMClient
    kb: KnowledgeBase
    memory: MemoryManager
    system_prompt: str
    rag_top_k: int
    rag_min_score: float
    max_tool_loops: int

    async def answer(self, chat_id: int, user_text: str) -> str:
        self.db.add_message(chat_id, "user", user_text)

        bundle = self.memory.build_memory_bundle(chat_id)
        rag_hits = self.kb.search(user_text, top_k=self.rag_top_k, min_score=self.rag_min_score)

        rag_text = format_knowledge_results(
            [{"source": hit.source, "text": hit.text} for hit in rag_hits]
        )

        messages: list[dict[str, str]] = [
            {"role": "system", "content": self.system_prompt},
        ]

        if bundle.summary:
            messages.append({"role": "system", "content": f"Память о диалоге:\n{bundle.summary}"})

        if rag_text and rag_text != "Ничего релевантного не найдено.":
            messages.append({"role": "system", "content": f"Релевантные материалы из базы знаний:\n{rag_text}"})

        for msg in bundle.recent_messages:
            messages.append(msg)

        messages.append(
            {
                "role": "system",
                "content": (
                    "Если тебе нужно выполнить действие, верни ТОЛЬКО JSON вида:\n"
                    '{"type":"tool","tool_name":"calculator","tool_args":{"expression":"2+2"}}\n'
                    "Если инструменты не нужны, верни обычный текст ответа."
                ),
            }
        )

        current_messages = messages
        last_response_text = ""

        for _ in range(self.max_tool_loops):
            response_text = await self.llm.generate_text(current_messages)
            last_response_text = response_text.strip()

            parsed = self.llm.try_parse_json(last_response_text)
            if not parsed or parsed.get("type") != "tool":
                self.db.add_message(chat_id, "assistant", last_response_text)
                await self.memory.maybe_summarize(chat_id)
                return last_response_text

            tool_name = str(parsed.get("tool_name", "")).strip()
            tool_args = parsed.get("tool_args", {})
            if not isinstance(tool_args, dict):
                tool_args = {}

            tool_result = execute_tool(
                tool_name,
                tool_args,
                rag_search_fn=lambda q: format_knowledge_results(
                    [{"source": h.source, "text": h.text} for h in self.kb.search(q, top_k=self.rag_top_k, min_score=self.rag_min_score)]
                ),
            )

            current_messages.append({"role": "assistant", "content": last_response_text})
            current_messages.append(
                {
                    "role": "system",
                    "content": f"Результат инструмента {tool_name}:\n{tool_result}",
                }
            )

        final_answer = "Не удалось сформировать ответ после нескольких попыток."
        self.db.add_message(chat_id, "assistant", final_answer)
        return final_answer
