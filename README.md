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



app.py
Главная точка входа Telegram-бота.

assistant_core.py
Оркестратор: собирает память, RAG, tools и LLM в один цикл.

config.py
Загрузка переменных окружения, настройка путей, параметров и лимитов.

db.py
SQLite-хранилище сообщений и резюме пользователя.

memory.py
Логика краткого long-term memory: что именно сохранять, как сжимать старый диалог.

rag.py
Индексирует файлы из knowledge/ и ищет релевантные куски текста.

tools.py
Инструменты, которые модель может вызывать.

llm.py
Абстракция над Gemma: локально через Ollama или через OpenAI-compatible endpoint.

ingest.py
Построение/обновление индекса базы знаний.

requirements.txt
Зависимости.

.env.example
Пример переменных окружения.

README.md
Инструкция по запуску.
