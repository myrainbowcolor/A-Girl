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

    按估算音节数把时长均分，每段一个"张口→闭合"周期，模拟真人说话节奏：
    长句音节多、开合次数多；短句更慢、更从容。仍保持确定性，便于无头测试。
    """
    seed = int(hashlib.md5(text.encode("utf-8")).hexdigest(), 16)
    syllables = estimate_syllables(text)
    cycles = max(syllables, duration_ms // cycle_ms)
    step = max(cycle_ms, duration_ms // cycles)
    frames: list[dict] = [{"t": 0, "v": 0.0}]
    for k in range(cycles):
        base = k * step
        if base >= duration_ms:
            break
        jitter = ((seed >> (k % 23)) & 0xFF) / 255.0
        # 句首/句尾略轻，中间音节张口更明显
        edge = 0.85 if 0 < k < cycles - 1 else 0.65
        open_v = round(min(0.95, (0.55 + 0.4 * jitter) * edge), 3)
        open_t = base + int(step * 0.32)
        close_t = min(duration_ms, base + int(step * 0.82))
        frames.append({"t": open_t, "v": open_v})
        frames.append({"t": close_t, "v": 0.0})
    frames.append({"t": duration_ms, "v": 0.0})
    return frames
