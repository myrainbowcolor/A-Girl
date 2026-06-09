"""语音子系统：TTS / STT 抽象与工厂。"""
from __future__ import annotations

from ..config import Settings
from .base import STTProvider, TTSProvider, TTSResult
from .mock import MockSTTProvider, MockTTSProvider
from .openai_compatible import OpenAICompatibleSTTProvider, OpenAICompatibleTTSProvider


def build_tts_provider(settings: Settings) -> TTSProvider:
    if settings.tts_provider == "openai_compatible" and settings.voice_api_key:
        return OpenAICompatibleTTSProvider(
            base_url=settings.voice_base_url,
            api_key=settings.voice_api_key,
            model=settings.tts_model,
            voice=settings.tts_voice,
            timeout=settings.llm_timeout_seconds,
        )
    return MockTTSProvider()


def build_stt_provider(settings: Settings) -> STTProvider:
    if settings.stt_provider == "openai_compatible" and settings.voice_api_key:
        return OpenAICompatibleSTTProvider(
            base_url=settings.voice_base_url,
            api_key=settings.voice_api_key,
            model=settings.stt_model,
            timeout=settings.llm_timeout_seconds,
        )
    return MockSTTProvider()


__all__ = [
    "TTSProvider",
    "STTProvider",
    "TTSResult",
    "MockTTSProvider",
    "MockSTTProvider",
    "OpenAICompatibleTTSProvider",
    "OpenAICompatibleSTTProvider",
    "build_tts_provider",
    "build_stt_provider",
]
