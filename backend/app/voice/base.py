"""语音 Provider 接口。"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class VoiceStyle:
    """情绪化语音风格（由 PAD 推导，传给 TTS）。"""
    rate: float = 1.0       # 语速倍率 0.5~1.5
    pitch: float = 1.0      # 音调倍率 0.5~1.5
    volume: float = 1.0     # 音量倍率 0~1.5
    style: str = "neutral"  # 语气标签：cheerful/gentle/sad/excited/neutral


@dataclass
class TTSResult:
    audio_base64: str
    format: str                       # wav | mp3 …
    duration_ms: int                  # 估算时长，供数字人口型/动画对齐
    provider: str
    lipsync: list[dict] = field(default_factory=list)   # 张口度轨迹 [{"t":ms,"v":0~1}]
    visemes: list[dict] = field(default_factory=list)   # viseme 口型序列
    style: dict | None = None          # 实际使用的语音风格


class TTSProvider(ABC):
    @abstractmethod
    def synthesize(
        self, text: str, voice: str | None = None, style: "VoiceStyle | None" = None
    ) -> TTSResult:
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
