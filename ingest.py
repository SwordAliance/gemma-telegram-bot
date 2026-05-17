"""Этот скрипт нужен, чтобы построить индекс знаний заранее."""
from __future__ import annotations

import asyncio

from config import load_settings
from rag import KnowledgeBase


def main() -> None:
    settings = load_settings()
    kb = KnowledgeBase(settings.knowledge_dir, settings.index_path)
    kb.rebuild()
    print(f"Index built at: {settings.index_path}")


if __name__ == "__main__":
    main()
