"""Этот файл скрывает способ подключения к Gemma"""
from __future__ import annotations

from dataclasses import dataclass
import json

import httpx


@dataclass
class LLMClient:
    backend: str
    ollama_base_url: str
    ollama_model: str
    openai_base_url: str
    openai_api_key: str
    openai_model: str
    request_timeout: float

    async def generate_text(self, messages: list[dict[str, str]], temperature: float = 0.7) -> str:
        if self.backend == "ollama":
            return await self._generate_ollama(messages, temperature)
        return await self._generate_openai_compatible(messages, temperature)

    async def _generate_ollama(self, messages: list[dict[str, str]], temperature: float) -> str:
        payload = {
            "model": self.ollama_model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature,
            },
        }
        async with httpx.AsyncClient(timeout=self.request_timeout) as client:
            resp = await client.post(f"{self.ollama_base_url}/api/chat", json=payload)
            resp.raise_for_status()
            data = resp.json()
            return data["message"]["content"]

    async def _generate_openai_compatible(self, messages: list[dict[str, str]], temperature: float) -> str:
        headers = {}
        if self.openai_api_key:
            headers["Authorization"] = f"Bearer {self.openai_api_key}"

        payload = {
            "model": self.openai_model,
            "messages": messages,
            "temperature": temperature,
        }

        async with httpx.AsyncClient(timeout=self.request_timeout, headers=headers) as client:
            resp = await client.post(f"{self.openai_base_url}/chat/completions", json=payload)
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"]

    @staticmethod
    def try_parse_json(text: str) -> dict | None:
        try:
            obj = json.loads(text)
            return obj if isinstance(obj, dict) else None
        except Exception:
            return None
