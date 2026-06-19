"""LLM Provider 抽象与工厂。"""
from __future__ import annotations

from ..config import Settings
from .base import LLMProvider
from .mock import MockLLMProvider
from .openai_compatible import OpenAICompatibleLLMProvider


def build_llm_provider(settings: Settings) -> LLMProvider:
    """构建 LLM。mock 仅用于 pytest/CI；用户聊天应配置 openai_compatible。"""
    if settings.llm_provider == "openai_compatible" and settings.llm_api_key:
        return OpenAICompatibleLLMProvider(
            base_url=settings.llm_base_url,
            api_key=settings.llm_api_key,
            model=settings.llm_model,
            timeout=settings.llm_timeout_seconds,
        )
    return MockLLMProvider()


__all__ = ["LLMProvider", "MockLLMProvider", "OpenAICompatibleLLMProvider", "build_llm_provider"]
