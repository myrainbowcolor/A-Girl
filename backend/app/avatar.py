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

    def live2d_params(self) -> dict[str, float]:
        """映射为 Live2D 标准参数，供嵌入游戏直接驱动 3D/2D 数字人。

        口型参数 ParamMouthOpenY 由 TTS 的 lipsync 轨迹逐帧驱动，这里给静态基线。
        """
        base = _LIVE2D_PRESETS.get(self.expression, _LIVE2D_PRESETS["平静"])
        k = self.intensity
        return {
            "ParamMouthForm": round(base["mouth_form"] * k, 3),   # 嘴角弧度（笑/撇）
            "ParamBrowLY": round(base["brow"] * k, 3),            # 眉毛高低
            "ParamBrowRY": round(base["brow"] * k, 3),
            "ParamEyeLOpen": base["eye_open"],
            "ParamEyeROpen": base["eye_open"],
            "ParamCheek": round(base["cheek"] * k, 3),            # 脸颊（脸红/鼓腮）
        }


# expression -> Live2D 表情基线（值域约 -1~1，正=上扬/睁大）
_LIVE2D_PRESETS = {
    "微笑": {"mouth_form": 1.0, "brow": 0.18, "eye_open": 0.9, "cheek": 0.42},
    "大笑": {"mouth_form": 1.0, "brow": 0.45, "eye_open": 0.62, "cheek": 0.72},
    "难过": {"mouth_form": -0.85, "brow": -0.65, "eye_open": 0.55, "cheek": 0.0},
    "担心": {"mouth_form": -0.35, "brow": -0.85, "eye_open": 1.05, "cheek": 0.05},
    "惊讶": {"mouth_form": 0.05, "brow": 0.85, "eye_open": 1.12, "cheek": 0.15},
    "平静": {"mouth_form": 0.18, "brow": 0.0, "eye_open": 0.95, "cheek": 0.08},
}


def emotion_to_avatar(emotion: EmotionState, is_crisis: bool = False) -> AvatarCue:
    """由 PAD 推导表情与动作。

    危机场景优先表现为"担心 + 安抚"，避免不合时宜的笑脸。
    """
    if is_crisis:
        return AvatarCue(expression="担心", intensity=0.9, animation="comfort")

    p, a = emotion.pleasure, emotion.arousal
    # 情绪越鲜明强度越高，弱情绪保留柔和底噪避免"面瘫"
    intensity = min(1.0, max(0.25, (abs(p) * 0.65 + abs(a) * 0.55) + 0.15))

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
