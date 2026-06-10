"""口型同步轨迹生成。

由文本与音频时长生成一串"嘴巴张合"关键帧，供数字人做口型同步：
- 独立模式前端用它驱动 SVG 嘴巴开合；
- 嵌入模式游戏用它驱动 Live2D 的 ParamMouthOpenY。

骨架阶段基于音节节奏的确定性近似；生产期可由真实 viseme 时序替换。
"""
from __future__ import annotations

import hashlib

_STEP_MS = 110     # 关键帧间隔（约一个音节）
_CYCLE_MS = 280    # 一个"张口→闭合"周期时长（约 3.5Hz，肉眼可辨）


def _is_cjk(ch: str) -> bool:
    return "\u4e00" <= ch <= "\u9fff"


def estimate_syllables(text: str) -> int:
    """粗略估算音节数：中文按字计，英文按词计。"""
    cjk = sum(1 for ch in text if _is_cjk(ch))
    words = len([w for w in text.split() if any(c.isalnum() for c in w) and not all(_is_cjk(c) for c in w)])
    return max(1, cjk + words)


def generate_lipsync(text: str, duration_ms: int, cycle_ms: int = _CYCLE_MS) -> list[dict]:
    """返回 [{"t": 毫秒, "v": 0~1 张口度}, ...]，首尾闭合。

    以固定节奏（约 3.5Hz）生成明确的"张口→闭合"循环，模拟真人说话：
    每个周期内嘴巴张开到峰值再完全合上，肉眼可清晰分辨开合，而非一直半张。
    节奏固定（不随文字长度变得过快），保证可观察性。
    """
    seed = int(hashlib.md5(text.encode("utf-8")).hexdigest(), 16)
    syllables = estimate_syllables(text)
    max_cycles = max(1, duration_ms // cycle_ms)
    # 音节数约束节奏，避免长句口型过快、短句口型过稀
    cycles = max(1, min(max_cycles, syllables))
    frames: list[dict] = [{"t": 0, "v": 0.0}]
    for k in range(cycles):
        base = k * cycle_ms
        jitter = ((seed >> (k % 23)) & 0xFF) / 255.0
        open_v = round(0.6 + 0.35 * jitter, 3)               # 张口峰值 0.6~0.95
        frames.append({"t": base + int(cycle_ms * 0.35), "v": open_v})  # 张口
        frames.append({"t": base + int(cycle_ms * 0.85), "v": 0.0})     # 闭合
    frames.append({"t": duration_ms, "v": 0.0})              # 结尾闭口
    return frames
