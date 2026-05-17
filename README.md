# Gemma Telegram Bot

Telegram-бот с Gemma, памятью, RAG и tool-calling.

## Возможности

- локальный запуск через Ollama
- облачный запуск через OpenAI-compatible endpoint
- SQLite-память
- RAG по папке knowledge/
- инструменты: calculator, current_time, search_knowledge


## Как использовать
складываете туда .txt, .md, .rst;
запускаете python ingest.py;
бот начинает искать ответы по этим текстам.
app.py - главная точка входа Telegram-бота.
assistant_core.py - оркестратор: собирает память, RAG, tools и LLM в один цикл.
config.py - загрузка переменных окружения, настройка путей, параметров и лимитов.
db.py - SQLite-хранилище сообщений и резюме пользователя.
memory.py - логика краткого long-term memory: что именно сохранять, как сжимать старый диалог.
rag.py - ндексируиет файлы из knowledge/ и ищет релевантные куски текста.
tools.py - инструменты, которые модель может вызывать.
llm.py - абстракция над Gemma: локально через Ollama или через OpenAI-compatible endpoint.
ingest.py построение/обновление индекса базы знаний.
requirements.txt - зависимости.
.env.example - пример переменных окружения.
README.md - инструкция по запуску.


## Установка

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt


