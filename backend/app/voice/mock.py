"""离线语音 Mock。

MockTTS 生成一段合法的静音 WAV（时长按文本长度估算），保证：
- 前端 <audio> 能正常加载/播放，链路可端到端验证；
- 数字人可用 duration_ms 对齐口型/动画。
MockSTT 返回占位转写，供无音频环境下跑通 STT 接口。
"""
from __future__ import annotations

import base64
import io
import struct

from dataclasses import asdict

from .base import STTProvider, TTSProvider, TTSResult, VoiceStyle
from .lipsync import generate_lipsync, generate_visemes

_SAMPLE_RATE = 16000
_MS_PER_CHAR = 140  # 估算每字朗读时长（基线，未计语速）


def _silent_wav(duration_ms: int, sample_rate: int = _SAMPLE_RATE) -> bytes:
    n_samples = max(1, int(sample_rate * duration_ms / 1000))
    data_size = n_samples * 2  # 16-bit mono
    buf = io.BytesIO()
    buf.write(b"RIFF")
    buf.write(struct.pack("<I", 36 + data_size))
    buf.write(b"WAVE")
    buf.write(b"fmt ")
    buf.write(struct.pack("<IHHIIHH", 16, 1, 1, sample_rate, sample_rate * 2, 2, 16))
    buf.write(b"data")
    buf.write(struct.pack("<I", data_size))
    buf.write(b"\x00\x00" * n_samples)
    return buf.getvalue()


from .tts_text import strip_for_tts


class MockTTSProvider(TTSProvider):
    @property
    def name(self) -> str:
        return "mock"

    def synthesize(
        self, text: str, voice: str | None = None, style: VoiceStyle | None = None
    ) -> TTSResult:
        text = strip_for_tts(text) or "嗯"
        style = style or VoiceStyle()
        # 语速影响时长（rate 越大越短）
        duration_ms = max(300, int(len(text) * _MS_PER_CHAR / max(0.3, style.rate)))
        wav = _silent_wav(duration_ms)
        return TTSResult(
            audio_base64=base64.b64encode(wav).decode("ascii"),
            format="wav",
            duration_ms=duration_ms,
            provider=self.name,
            lipsync=generate_lipsync(text, duration_ms),
            visemes=generate_visemes(text, duration_ms),
            style=asdict(style),
        )


class MockSTTProvider(STTProvider):
    @property
    def name(self) -> str:
        return "mock"

    def transcribe(self, audio_base64: str, fmt: str = "wav") -> str:
        # 离线占位：真实环境由 OpenAI 兼容 STT 替换
        return "（语音转写占位文本）"
