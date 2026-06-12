"""情绪化语音风格：由 PAD 情绪推导 TTS 的语速/音调/音量/语气。

让语音"听起来有情绪"：开心更快更高更亮，难过更慢更低更轻。
生产期可把 style 映射到各 TTS 厂商的风格参数（如 Azure 的 speaking style、
OpenAI 的 voice instructions）。
"""
from __future__ import annotations

from ..domain import EmotionState
from .base import VoiceStyle


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


def style_from_emotion(
    emotion: EmotionState,
    is_crisis: bool = False,
    user_sentiment: float | None = None,
) -> VoiceStyle:
    if is_crisis:
        # 危机：放慢、压低、轻柔，体现关切与安抚
        return VoiceStyle(rate=0.85, pitch=0.95, volume=0.9, style="gentle")

    p, a = emotion.pleasure, emotion.arousal
    # 激活度↑→语速/音量↑；愉悦度↑→音调↑
    rate = _clamp(1.0 + 0.25 * a + 0.1 * p, 0.6, 1.4)
    pitch = _clamp(1.0 + 0.2 * p + 0.05 * a, 0.7, 1.35)
    volume = _clamp(0.9 + 0.25 * a, 0.6, 1.3)

    if p >= 0.3 and a >= 0.4:
        style = "excited"
    elif p >= 0.3:
        style = "cheerful"
    elif p <= -0.3:
        style = "sad"
    else:
        style = "neutral"

    # 用户本轮低落时，语气放慢放轻，避免「开心腔」安慰人
    if user_sentiment is not None and user_sentiment < -0.2:
        rate = min(rate, 0.92)
        pitch = min(pitch, 1.02)
        volume = min(volume, 0.95)
        if style in ("excited", "cheerful"):
            style = "gentle"

    return VoiceStyle(
        rate=round(rate, 3), pitch=round(pitch, 3), volume=round(volume, 3), style=style
    )
