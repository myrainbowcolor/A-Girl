"""数字人形象：将内部 PAD 情绪映射为可驱动形象的表情/动作线索。

独立模式下前端用简单头像展示；嵌入模式下游戏用这些线索驱动 Live2D/3D 数字人。
"""
from __future__ import annotations

from dataclasses import dataclass

from .domain import EmotionState


@dataclass
class AvatarCue:
    expression: str   # 表情：微笑/大笑/难过/担心/惊讶/平静
    intensity: float  # 表情强度 0~1
    animation: str    # 建议肢体动作：idle/wave/nod/comfort/cheer


def emotion_to_avatar(emotion: EmotionState, is_crisis: bool = False) -> AvatarCue:
    """由 PAD 推导表情与动作。

    危机场景优先表现为"担心 + 安抚"，避免不合时宜的笑脸。
    """
    if is_crisis:
        return AvatarCue(expression="担心", intensity=0.9, animation="comfort")

    p, a = emotion.pleasure, emotion.arousal
    intensity = min(1.0, (abs(p) + abs(a)) / 2 + 0.2)

    if p >= 0.3 and a >= 0.45:
        return AvatarCue(expression="大笑", intensity=intensity, animation="cheer")
    if p >= 0.3:
        return AvatarCue(expression="微笑", intensity=intensity, animation="nod")
    if p <= -0.3 and a >= 0.45:
        return AvatarCue(expression="担心", intensity=intensity, animation="comfort")
    if p <= -0.3:
        return AvatarCue(expression="难过", intensity=intensity, animation="idle")
    if a >= 0.6:
        return AvatarCue(expression="惊讶", intensity=intensity, animation="idle")
    return AvatarCue(expression="平静", intensity=max(0.2, intensity), animation="idle")
