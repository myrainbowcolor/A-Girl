"""OpenAI 兼容 Chat Completions Provider。

可对接 OpenAI、DeepSeek、通义千问(兼容模式)、智谱等任何提供 /chat/completions 的服务。
"""
from __future__ import annotations

import json
from collections.abc import Iterator

import httpx

from .base import LLMProvider


class OpenAICompatibleLLMProvider(LLMProvider):
    def __init__(self, base_url: str, api_key: str, model: str, timeout: float = 120.0) -> None:
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key
        self._model = model
        self._timeout = timeout

    @property
    def name(self) -> str:
        return f"openai_compatible:{self._model}"

    def _headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self._api_key}", "Content-Type": "application/json"}

    def _payload(self, system_prompt: str, messages: list[dict], temperature: float, stream: bool) -> dict:
        return {
            "model": self._model,
            "messages": [{"role": "system", "content": system_prompt}, *messages],
            "temperature": temperature,
            "stream": stream,
        }

    def generate(self, system_prompt: str, messages: list[dict], temperature: float = 0.8) -> str:
        with httpx.Client(timeout=self._timeout) as client:
            resp = client.post(
                f"{self._base_url}/chat/completions",
                json=self._payload(system_prompt, messages, temperature, stream=False),
                headers=self._headers(),
            )
            resp.raise_for_status()
            data = resp.json()
        return data["choices"][0]["message"]["content"].strip()

    def generate_stream(
        self, system_prompt: str, messages: list[dict], temperature: float = 0.8
    ) -> Iterator[str]:
        with httpx.Client(timeout=self._timeout) as client:
            with client.stream(
                "POST",
                f"{self._base_url}/chat/completions",
                json=self._payload(system_prompt, messages, temperature, stream=True),
                headers=self._headers(),
            ) as resp:
                resp.raise_for_status()
                for line in resp.iter_lines():
                    if not line or not line.startswith("data: "):
                        continue
                    payload = line[6:].strip()
                    if payload == "[DONE]":
                        break
                    try:
                        data = json.loads(payload)
                    except json.JSONDecodeError:
                        continue
                    choices = data.get("choices") or []
                    if not choices:
                        continue
                    delta = choices[0].get("delta") or {}
                    piece = delta.get("content")
                    if piece:
                        yield piece
