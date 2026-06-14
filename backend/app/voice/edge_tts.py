"""Edge TTS Provider — 免费微软神经语音（无需 API Key）。

使用 edge-tts 调用 Microsoft Edge Read Aloud 服务，支持高质量中文女声。
"""
from __future__ import annotations

import asyncio
import base64
import concurrent.futures
from dataclasses import asdict
from io import BytesIO

from .base import TTSProvider, TTSResult, VoiceStyle
from .lipsync import generate_lipsync, generate_visemes

# 小语默认：晓晓，温柔自然的中文女声
DEFAULT_VOICE = "zh-CN-XiaoxiaoNeural"
_MS_PER_CHAR = 140


def _rate_str(rate: float) -> str:
    pct = int(round((rate - 1.0) * 100))
    pct = max(-50, min(50, pct))
    return f"{pct:+d}%"


def _pitch_str(pitch: float) -> str:
    hz = int(round((pitch - 1.0) * 40))
    hz = max(-30, min(30, hz))
    return f"{hz:+d}Hz"


def _mp3_duration_ms(data: bytes, text: str, rate: float = 1.0) -> int:
    try:
        from mutagen.mp3 import MP3

        return max(300, int(MP3(BytesIO(data)).info.length * 1000))
    except Exception:
        return max(300, int(len(text) * _MS_PER_CHAR / max(0.3, rate)))


async def _synthesize_async(text: str, voice: str, rate: str, pitch: str) -> bytes:
    import edge_tts

    communicate = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)
    chunks: list[bytes] = []
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            chunks.append(chunk["data"])
    return b"".join(chunks)


def _run_async(coro):
    """在 FastAPI 已有事件循环时安全运行 async TTS。"""
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
        return pool.submit(asyncio.run, coro).result()


from .tts_text import strip_for_tts


class EdgeTTSProvider(TTSProvider):
    def __init__(self, voice: str = DEFAULT_VOICE) -> None:
        self._voice = voice

    @property
    def name(self) -> str:
        return f"edge:{self._voice}"

    def synthesize(
        self, text: str, voice: str | None = None, style: VoiceStyle | None = None
    ) -> TTSResult:
        text = strip_for_tts(text) or "嗯"
        style = style or VoiceStyle()
        v = voice or self._voice
        rate = _rate_str(style.rate)
        pitch = _pitch_str(style.pitch)
        audio = _run_async(_synthesize_async(text, v, rate, pitch))
        if not audio:
            raise RuntimeError("edge-tts returned empty audio")
        duration_ms = _mp3_duration_ms(audio, text, style.rate)
        return TTSResult(
            audio_base64=base64.b64encode(audio).decode("ascii"),
            format="mp3",
            duration_ms=duration_ms,
            provider=self.name,
            lipsync=generate_lipsync(text, duration_ms),
            visemes=generate_visemes(text, duration_ms),
            style=asdict(style),
        )
