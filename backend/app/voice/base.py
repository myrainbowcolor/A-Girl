"""语音 Provider 接口。"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class TTSResult:
    audio_base64: str
    format: str                       # wav | mp3 …
    duration_ms: int                  # 估算时长，供数字人口型/动画对齐
    provider: str
    lipsync: list[dict] = field(default_factory=list)  # 口型轨迹 [{"t":ms,"v":0~1}]


class TTSProvider(ABC):
    @abstractmethod
    def synthesize(self, text: str, voice: str | None = None) -> TTSResult:
        raise NotImplementedError

    @property
    @abstractmethod
    def name(self) -> str:
        raise NotImplementedError


class STTProvider(ABC):
    @abstractmethod
    def transcribe(self, audio_base64: str, fmt: str = "wav") -> str:
        raise NotImplementedError

    @property
    @abstractmethod
    def name(self) -> str:
        raise NotImplementedError
