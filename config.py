"""Application configuration for the Gemma Telegram bot."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os


def _env(name: str, default: str | None = None) -> str:
    value = os.getenv(name, default)
    if value is None or value.strip() == "":
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value.strip()


def _env_int(name: str, default: int) -> int:
    raw = os.getenv(name, str(default)).strip()
    try:
        return int(raw)
    except ValueError as exc:
        raise RuntimeError(f"Environment variable {name} must be an integer, got {raw!r}") from exc


def _env_float(name: str, default: float) -> float:
    raw = os.getenv(name, str(default)).strip()
    try:
        return float(raw)
    except ValueError as exc:
        raise RuntimeError(f"Environment variable {name} must be a float, got {raw!r}") from exc


@dataclass(frozen=True)
class Settings:
    telegram_token: str
    backend: str
    ollama_base_url: str
    ollama_model: str
    openai_base_url: str
    openai_api_key: str
    openai_model: str
    system_prompt: str
    max_history_messages: int
    temperature: float
    request_timeout: float
    data_dir: Path
    knowledge_dir: Path
    index_path: Path
    db_path: Path
    rag_top_k: int
    rag_min_score: float
    summary_trigger_messages: int
    max_tool_loops: int


def load_settings() -> Settings:
    backend = os.getenv("LLM_BACKEND", "ollama").strip().lower()
    if backend not in {"ollama", "openai_compatible"}:
        raise RuntimeError("LLM_BACKEND must be either 'ollama' or 'openai_compatible'.")

    data_dir = Path(os.getenv("DATA_DIR", "data")).expanduser().resolve()
    knowledge_dir = Path(os.getenv("KNOWLEDGE_DIR", "knowledge")).expanduser().resolve()
    data_dir.mkdir(parents=True, exist_ok=True)
    knowledge_dir.mkdir(parents=True, exist_ok=True)

    return Settings(
        telegram_token=_env("TELEGRAM_BOT_TOKEN"),
        backend=backend,
        ollama_base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").strip(),
        ollama_model=os.getenv("OLLAMA_MODEL", "gemma3:1b").strip(),
        openai_base_url=os.getenv("OPENAI_BASE_URL", "http://localhost:8000/v1").strip(),
        openai_api_key=os.getenv("OPENAI_API_KEY", "").strip(),
        openai_model=os.getenv("OPENAI_MODEL", "gemma").strip(),
        system_prompt=os.getenv(
            "SYSTEM_PROMPT",
            "Ты вежливый, понятный и полезный ассистент. Отвечай по-русски, если пользователь пишет по-русски.",
        ).strip(),
        max_history_messages=_env_int("MAX_HISTORY_MESSAGES", 16),
        temperature=_env_float("TEMPERATURE", 0.7),
        request_timeout=_env_float("REQUEST_TIMEOUT", 120.0),
        data_dir=data_dir,
        knowledge_dir=knowledge_dir,
        index_path=data_dir / "kb_index.joblib",
        db_path=data_dir / "memory.sqlite3",
        rag_top_k=_env_int("RAG_TOP_K", 4),
        rag_min_score=_env_float("RAG_MIN_SCORE", 0.12),
        summary_trigger_messages=_env_int("SUMMARY_TRIGGER_MESSAGES", 30),
        max_tool_loops=_env_int("MAX_TOOL_LOOPS", 3),
    )
