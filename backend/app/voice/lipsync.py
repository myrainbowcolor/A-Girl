"""口型同步轨迹生成（含 viseme 级嘴型）。

由文本与音频时长生成两类数据，供数字人做口型同步：
- lipsync：单维"张口度"轨迹（兼容旧前端 / Live2D ParamMouthOpenY）；
- visemes：按音节的口型序列（A/E/I/O/U/MBP/REST），更接近真人发音的嘴型。

骨架阶段基于音节节奏 + 近似元音判定；生产期可由 TTS 返回的真实 viseme 时序替换。
"""
from __future__ import annotations

import hashlib

_STEP_MS = 110     # 关键帧间隔（约一个音节）
_CYCLE_MS = 280    # 一个"张口→闭合"周期时长（约 3.5Hz，肉眼可辨）

# viseme 口型 → 张口度(open) 与 嘴宽(wide, -1窄/圆 ~ 1扁/宽)
VISEME_SHAPES: dict[str, dict[str, float]] = {
    "REST": {"open": 0.0, "wide": 0.0},   # 闭合/停顿
    "MBP": {"open": 0.0, "wide": 0.1},    # m/b/p 闭唇
    "A": {"open": 0.95, "wide": 0.2},     # 啊 大张
    "E": {"open": 0.5, "wide": 0.8},      # 诶 扁宽
    "I": {"open": 0.3, "wide": 0.9},      # 衣 扁窄
    "O": {"open": 0.7, "wide": -0.6},     # 哦 圆
    "U": {"open": 0.35, "wide": -0.9},    # 乌 圆小
}

# 拼音韵母主元音 → viseme（用于把汉字粗略映射到口型）
_FINAL_TO_VISEME = [
    ("iao", "A"), ("iang", "A"), ("uang", "A"), ("uai", "A"), ("ang", "A"),
    ("ian", "E"), ("uan", "A"), ("eng", "E"), ("ing", "I"), ("ong", "O"),
    ("ao", "A"), ("ai", "A"), ("an", "A"), ("ei", "E"), (" en", "E"),
    ("ou", "O"), ("ui", "E"), ("un", "U"), ("ie", "E"), ("ue", "E"),
    ("iu", "O"), ("er", "E"),
    ("a", "A"), ("o", "O"), ("e", "E"), ("i", "I"), ("u", "U"), ("v", "U"),
]


def _is_cjk(ch: str) -> bool:
    return "\u4e00" <= ch <= "\u9fff"


def estimate_syllables(text: str) -> int:
    """粗略估算音节数：中文按字计，英文按词计。"""
    cjk = sum(1 for ch in text if _is_cjk(ch))
    words = len([w for w in text.split() if any(c.isalnum() for c in w) and not all(_is_cjk(c) for c in w)])
    return max(1, cjk + words)


_VOWEL_VISEME = {"a": "A", "e": "E", "i": "I", "o": "O", "u": "U"}
_CJK_VISEME_RING = ["A", "O", "E", "I", "U"]  # 无拼音词典时的确定性近似


def text_to_visemes(text: str) -> list[str]:
    """把文本转成逐音节的 viseme 序列（元音口型 + 闭唇）。

    - 英文：取每个词的元音字母映射；含 m/b/p 起始词加一个闭唇帧。
    - 中文：无内置拼音词典，用字符确定性散列映射到元音口型环，保证稳定且有变化。
    """
    visemes: list[str] = []
    for ch in text:
        if _is_cjk(ch):
            idx = ord(ch) % len(_CJK_VISEME_RING)
            visemes.append(_CJK_VISEME_RING[idx])
        elif ch.isalpha():
            low = ch.lower()
            if low in _VOWEL_VISEME:
                visemes.append(_VOWEL_VISEME[low])
            elif low in ("m", "b", "p"):
                visemes.append("MBP")
        # 标点/空格视为停顿
        elif ch.strip() == "" or ch in "，。！？、,.!?…":
            if visemes and visemes[-1] != "REST":
                visemes.append("REST")
    return visemes or ["A"]


def generate_visemes(text: str, duration_ms: int) -> list[dict]:
    """返回按时间排布的 viseme 关键帧：
    [{"t": ms, "viseme": "A", "open": 0.95, "wide": 0.2}, ...]，首尾闭合。
    """
    seq = text_to_visemes(text)
    n = len(seq)
    per = duration_ms / n
    frames: list[dict] = [{"t": 0, "viseme": "REST", **VISEME_SHAPES["REST"]}]
    for i, v in enumerate(seq):
        shape = VISEME_SHAPES[v]
        # 音节中部呈现该 viseme
        frames.append({"t": round(i * per + per * 0.45), "viseme": v, **shape})
        # 音节间短暂收口，制造开合节奏
        if i < n - 1:
            frames.append({"t": round((i + 1) * per - per * 0.12), "viseme": "REST",
                           **VISEME_SHAPES["REST"]})
    frames.append({"t": duration_ms, "viseme": "REST", **VISEME_SHAPES["REST"]})
    return frames


def _pause_ms_at(text: str, cycle_index: int) -> int:
    """在标点处插入短暂停顿，模拟语流中的自然间歇。"""
    if not text:
        return 0
    punct = "，。！？、,.!?…"
    hits = [i for i, ch in enumerate(text) if ch in punct]
    if not hits:
        return 0
    pos = hits[cycle_index % len(hits)]
    # 标点越靠后，停顿略长
    return 40 + (pos % 3) * 25


def generate_lipsync(text: str, duration_ms: int, cycle_ms: int = _CYCLE_MS) -> list[dict]:
    """返回 [{"t": 毫秒, "v": 0~1 张口度}, ...]，首尾闭合。

    以固定节奏（约 3.5Hz）生成明确的"张口→闭合"循环，模拟真人说话：
    每个周期内嘴巴张开到峰值再完全合上；标点处插入短暂停顿，更接近自然语流。
    """
    seed = int(hashlib.md5(text.encode("utf-8")).hexdigest(), 16)
    cycles = max(1, duration_ms // cycle_ms)
    frames: list[dict] = [{"t": 0, "v": 0.0}]
    t_cursor = 0
    for k in range(cycles):
        pause = _pause_ms_at(text, k)
        base = t_cursor + pause
        if base >= duration_ms:
            break
        jitter = ((seed >> (k % 23)) & 0xFF) / 255.0
        # 轻声/语气词张口略小，重读略大
        open_v = round(0.55 + 0.4 * jitter, 3)
        open_t = min(duration_ms, base + int(cycle_ms * 0.35))
        close_t = min(duration_ms, base + int(cycle_ms * 0.85))
        frames.append({"t": open_t, "v": open_v})
        frames.append({"t": close_t, "v": 0.0})
        t_cursor = base + cycle_ms
    frames.append({"t": duration_ms, "v": 0.0})
    # 去重并按时间排序，保证单调递增
    frames.sort(key=lambda f: f["t"])
    deduped: list[dict] = []
    for f in frames:
        if deduped and deduped[-1]["t"] == f["t"]:
            deduped[-1] = f
        else:
            deduped.append(f)
    return deduped
