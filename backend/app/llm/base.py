"""LLM Provider 接口。"""
from __future__ import annotations

from abc import ABC, abstractmethod


class LLMProvider(ABC):
    @abstractmethod
    def generate(self, system_prompt: str, messages: list[dict], temperature: float = 0.8) -> str:
        """根据 system 提示与对话历史生成回复。

        messages: [{"role": "user"|"assistant", "content": str}, ...]
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def name(self) -> str:
        raise NotImplementedError
