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

    按音节数在时长内均匀分布张口峰值，模拟说话节奏；同一文本输出确定。
    """
    seed = int(hashlib.md5(text.encode("utf-8")).hexdigest(), 16)
    syllables = estimate_syllables(text)
    max_cycles = max(1, duration_ms // cycle_ms)
    cycles = min(max_cycles, max(1, syllables))

    frames: list[dict] = [{"t": 0, "v": 0.0}]
    if cycles == 1:
        jitter = (seed & 0xFF) / 255.0
        open_v = round(0.55 + 0.4 * jitter, 3)
        mid = duration_ms // 2
        frames.append({"t": max(40, mid - 60), "v": open_v})
        frames.append({"t": min(duration_ms - 20, mid + 60), "v": 0.0})
    else:
        span = max(cycle_ms, duration_ms // cycles)
        for k in range(cycles):
            base = k * span
            if base >= duration_ms - 40:
                break
            jitter = ((seed >> (k % 23)) & 0xFF) / 255.0
            open_v = round(0.55 + 0.4 * jitter, 3)
            open_t = base + int(span * 0.35)
            close_t = base + int(span * 0.82)
            frames.append({"t": open_t, "v": open_v})
            frames.append({"t": min(close_t, duration_ms - 10), "v": 0.0})

    frames.append({"t": duration_ms, "v": 0.0})
    # 去重并按时间排序，保证单调
    frames = sorted({f["t"]: f for f in frames}.values(), key=lambda x: x["t"])
    return frames
