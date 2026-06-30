"""数字人形象：将内部 PAD 情绪映射为可驱动形象的表情/动作线索。

独立模式下前端用简单头像展示；嵌入模式下游戏用这些线索驱动 Live2D/3D 数字人。
"""
from __future__ import annotations

from dataclasses import dataclass

from .domain import EmotionState

# 整句中性封闭极简口语：陪伴脸应平静，不因前轮正向 PAD 误微笑（不含「不想说」类情绪封闭句）
_NEUTRAL_MINIMAL_AVATAR = frozenset({
    "..", "...", "…", "。", "嗯", "嗯嗯", "哦", "噢", "额", "好", "行", "算了", "随便",
})


def is_neutral_minimal_avatar_utterance(text: str) -> bool:
    """整句仅为中性极简口语（嗯/哦等），非 masking/回避/情绪封闭倾诉。"""
    t = text.strip()
    return t in _NEUTRAL_MINIMAL_AVATAR


@dataclass
class AvatarCue:
    expression: str   # 表情：微笑/大笑/难过/担心/惊讶/平静
    intensity: float  # 表情强度 0~1
    animation: str    # 建议肢体动作：idle/wave/nod/comfort/cheer

    def live2d_params(self) -> dict[str, float]:
        """映射为 Live2D 标准参数，供嵌入游戏直接驱动 3D/2D 数字人。

        口型参数 ParamMouthOpenY 由 TTS 的 lipsync 轨迹逐帧驱动，这里给静态基线。
        intensity 做非线性映射，弱情绪更含蓄、强情绪更明显，避免"半永久尬笑"。
        """
        base = _LIVE2D_PRESETS.get(self.expression, _LIVE2D_PRESETS["平静"])
        k = _intensity_curve(max(0.15, min(1.0, self.intensity)))
        eye_smile = base.get("eye_smile", 0.0) * k
        return {
            "ParamMouthForm": round(base["mouth_form"] * k, 3),   # 嘴角弧度（笑/撇）
            "ParamBrowLY": round(base["brow"] * k, 3),            # 眉毛高低
            "ParamBrowRY": round(base["brow"] * k, 3),
            "ParamEyeLOpen": round(base["eye_open"] * (0.85 + 0.15 * k), 3),
            "ParamEyeROpen": round(base["eye_open"] * (0.85 + 0.15 * k), 3),
            "ParamEyeLSmile": round(eye_smile, 3),                # 笑眼
            "ParamEyeRSmile": round(eye_smile, 3),
            "ParamCheek": round(base["cheek"] * k, 3),            # 脸颊（脸红/鼓腮）
        }


def _intensity_curve(raw: float) -> float:
    """S 形强度曲线：中段变化细腻，高段不过饱和。"""
    x = max(0.0, min(1.0, raw))
    return round(x * x * (3.0 - 2.0 * x), 3)


# expression -> Live2D 表情基线（值域约 -1~1，正=上扬/睁大）
_LIVE2D_PRESETS = {
    "微笑": {"mouth_form": 1.0, "brow": 0.2, "eye_open": 1.0, "cheek": 0.35, "eye_smile": 0.5},
    "大笑": {"mouth_form": 1.0, "brow": 0.4, "eye_open": 0.65, "cheek": 0.65, "eye_smile": 0.85},
    "难过": {"mouth_form": -0.8, "brow": -0.6, "eye_open": 0.55, "cheek": 0.0, "eye_smile": 0.0},
    "担心": {"mouth_form": -0.45, "brow": -0.85, "eye_open": 1.08, "cheek": 0.0, "eye_smile": 0.0},
    "惊讶": {"mouth_form": 0.0, "brow": 0.85, "eye_open": 1.15, "cheek": 0.1, "eye_smile": 0.0},
    "平静": {"mouth_form": 0.2, "brow": 0.0, "eye_open": 1.0, "cheek": 0.05, "eye_smile": 0.1},
}


def emotion_to_avatar(
    emotion: EmotionState,
    is_crisis: bool = False,
    user_sentiment: float | None = None,
    user_text: str | None = None,
) -> AvatarCue:
    """由 PAD 推导表情与动作。

    危机场景优先表现为"担心 + 安抚"，避免不合时宜的笑脸。
    user_sentiment：用户本轮情感倾向；负向时 NPC 优先展示倾听/安抚姿态。
    user_text：封闭极简句（嗯/哦等）优先平静陪伴脸，不因前轮正向 PAD 误微笑。
    """
    if is_crisis:
        return AvatarCue(expression="担心", intensity=0.9, animation="comfort")

    if user_text is not None and is_neutral_minimal_avatar_utterance(user_text):
        p, a = emotion.pleasure, emotion.arousal
        raw = min(1.0, max(0.2, (abs(p) + abs(a)) / 1.6 + 0.1))
        return AvatarCue(expression="平静", intensity=_intensity_curve(raw), animation="idle")

    if user_sentiment is not None and user_sentiment < -0.2:
        p, a = emotion.pleasure, emotion.arousal
        intensity = min(1.0, (abs(p) + abs(a)) / 2 + 0.35)
        return AvatarCue(expression="担心", intensity=intensity, animation="comfort")

    # 用户分享好事时，NPC 展现共情式喜悦（倾听 + 微笑），而非呆板平静脸
    if user_sentiment is not None and user_sentiment > 0.35:
        a = emotion.arousal
        raw_intensity = min(1.0, max(0.35, user_sentiment * 0.45 + 0.3))
        intensity = _intensity_curve(raw_intensity)
        if user_sentiment > 0.6 and a >= 0.3:
            return AvatarCue(expression="大笑", intensity=intensity, animation="cheer")
        return AvatarCue(expression="微笑", intensity=intensity, animation="nod")

    p, a = emotion.pleasure, emotion.arousal
    # 情绪越鲜明，表情幅度越大；弱情绪也保留最低可见度
    raw_intensity = min(1.0, max(0.25, (abs(p) + abs(a)) / 1.6 + 0.15))
    intensity = _intensity_curve(raw_intensity)

    if p >= 0.3 and a >= 0.45:
        return AvatarCue(expression="大笑", intensity=intensity, animation="cheer")
    if p >= 0.3:
        return AvatarCue(expression="微笑", intensity=intensity, animation="nod")
    if p <= -0.3 and a >= 0.45:
        return AvatarCue(expression="担心", intensity=intensity, animation="comfort")
    if p <= -0.3:
        return AvatarCue(expression="难过", intensity=intensity, animation="comfort")
    if a >= 0.6:
        return AvatarCue(expression="惊讶", intensity=intensity, animation="idle")
    return AvatarCue(expression="平静", intensity=max(0.2, intensity), animation="idle")
