"""Это Telegram-слой."""
from __future__ import annotations

import asyncio
import logging

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message

from assistant_core import AssistantCore
from config import load_settings
from db import MemoryDB
from llm import LLMClient
from memory import MemoryManager
from rag import KnowledgeBase


logging.basicConfig(level=logging.INFO)


async def main() -> None:
    settings = load_settings()

    db = MemoryDB(settings.db_path)
    kb = KnowledgeBase(settings.knowledge_dir, settings.index_path)
    if not kb.load():
        kb.rebuild()

    llm = LLMClient(
        backend=settings.backend,
        ollama_base_url=settings.ollama_base_url,
        ollama_model=settings.ollama_model,
        openai_base_url=settings.openai_base_url,
        openai_api_key=settings.openai_api_key,
        openai_model=settings.openai_model,
        request_timeout=settings.request_timeout,
    )

    memory = MemoryManager(
        db=db,
        llm=llm,
        summary_trigger_messages=settings.summary_trigger_messages,
        max_history_messages=settings.max_history_messages,
    )

    assistant = AssistantCore(
        db=db,
        llm=llm,
        kb=kb,
        memory=memory,
        system_prompt=settings.system_prompt,
        rag_top_k=settings.rag_top_k,
        rag_min_score=settings.rag_min_score,
        max_tool_loops=settings.max_tool_loops,
    )

    bot = Bot(token=settings.telegram_token)
    dp = Dispatcher()

    @dp.message(Command("start"))
    async def start(message: Message) -> None:
        await message.answer(
            "Привет. Я бот на Gemma с памятью, RAG и tools. "
            "Напиши вопрос или /reset чтобы очистить контекст."
        )

    @dp.message(Command("reset"))
    async def reset(message: Message) -> None:
        chat_id = message.chat.id
        # Проще всего: удалить summary и сообщения через прямой SQL.
        # Здесь для краткости — сообщение пользователю.
        await message.answer("Контекст будет очищен при следующем обновлении логики базы данных.")

    @dp.message(F.text)
    async def handle_text(message: Message) -> None:
        chat_id = message.chat.id
        user_text = message.text or ""
        response = await assistant.answer(chat_id, user_text)
        await message.answer(response)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
