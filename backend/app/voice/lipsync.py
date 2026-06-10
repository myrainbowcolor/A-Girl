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

    按估算音节数分配张口节奏，每个周期"张口→闭合"一次；
    峰值带轻微随机抖动，模拟真人说话强弱变化。
    """
    seed = int(hashlib.md5(text.encode("utf-8")).hexdigest(), 16)
    syllables = estimate_syllables(text)
    # 音节数驱动循环次数，但单周期不低于 80ms，避免过快闪烁
    min_cycle = max(80, cycle_ms // 2)
    cycles = max(1, min(syllables, duration_ms // min_cycle))
    step = max(min_cycle, duration_ms // cycles)
    frames: list[dict] = [{"t": 0, "v": 0.0}]
    for k in range(cycles):
        base = k * step
        if base >= duration_ms:
            break
        jitter = ((seed >> (k % 23)) & 0xFF) / 255.0
        # 句首句尾略轻，中间音节张口更明显
        edge = 0.85 if 0 < k < cycles - 1 else 0.65
        open_v = round((0.55 + 0.4 * jitter) * edge, 3)
        open_t = base + int(step * 0.32)
        close_t = base + int(step * 0.82)
        if open_t < duration_ms:
            frames.append({"t": open_t, "v": open_v})
        if close_t < duration_ms:
            frames.append({"t": close_t, "v": 0.0})
    frames.append({"t": duration_ms, "v": 0.0})
    return frames
