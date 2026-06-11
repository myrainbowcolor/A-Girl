"""LLM Provider 接口。"""
from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterator


class LLMProvider(ABC):
    @abstractmethod
    def generate(self, system_prompt: str, messages: list[dict], temperature: float = 0.8) -> str:
        """根据 system 提示与对话历史生成回复。

        messages: [{"role": "user"|"assistant", "content": str}, ...]
        """
        raise NotImplementedError

    def generate_stream(
        self, system_prompt: str, messages: list[dict], temperature: float = 0.8
    ) -> Iterator[str]:
        """流式生成；默认一次性产出后按块切分。"""
        text = self.generate(system_prompt, messages, temperature=temperature)
        step = max(1, len(text) // 24)
        for i in range(0, len(text), step):
            yield text[i : i + step]

    @property
    @abstractmethod
    def name(self) -> str:
        raise NotImplementedError
