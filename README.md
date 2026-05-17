# Gemma Telegram Bot

Telegram-бот с Gemma, памятью, RAG и tool-calling.

## Возможности

- локальный запуск через Ollama
- облачный запуск через OpenAI-compatible endpoint
- SQLite-память
- RAG по папке knowledge/
- инструменты: calculator, current_time, search_knowledge

## Установка

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
