"""OpenAI 兼容 Chat Completions Provider。

可对接 OpenAI、DeepSeek、通义千问(兼容模式)、智谱等任何提供 /chat/completions 的服务。
"""
from __future__ import annotations

import httpx

from .base import LLMProvider


class OpenAICompatibleLLMProvider(LLMProvider):
    def __init__(self, base_url: str, api_key: str, model: str, timeout: float = 30.0) -> None:
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key
        self._model = model
        self._timeout = timeout

    @property
    def name(self) -> str:
        return f"openai_compatible:{self._model}"

    def generate(self, system_prompt: str, messages: list[dict], temperature: float = 0.8) -> str:
        payload = {
            "model": self._model,
            "messages": [{"role": "system", "content": system_prompt}, *messages],
            "temperature": temperature,
        }
        headers = {"Authorization": f"Bearer {self._api_key}", "Content-Type": "application/json"}
        with httpx.Client(timeout=self._timeout) as client:
            resp = client.post(f"{self._base_url}/chat/completions", json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()
        return data["choices"][0]["message"]["content"].strip()
