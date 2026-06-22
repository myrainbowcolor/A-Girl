"""情感关键词匹配：避免「不开心」误命中「开心」等否定冲突。"""
from __future__ import annotations

# keyword -> 否定前缀/完整否定词
_NEGATION_BLOCK: dict[str, tuple[str, ...]] = {
    "开心": ("不开心", "不太开心", "不怎么开心"),
    "高兴": ("不高兴", "不太高兴"),
    "喜欢": ("不喜欢", "不太喜欢"),
    "幸福": ("不幸福",),
    "温暖": ("不温暖",),
}


def contains_keyword(text: str, keyword: str) -> bool:
    """text 含 keyword，且不被常见否定形式抵消。"""
    if keyword not in text:
        return False
    for neg in _NEGATION_BLOCK.get(keyword, ()):
        if neg in text:
            return False
    return True


def contains_any(text: str, keywords: tuple[str, ...] | list[str]) -> bool:
    return any(contains_keyword(text, k) for k in keywords)


POSITIVE_WORDS = (
    "开心", "高兴", "喜欢", "谢谢", "哈哈", "棒", "幸福", "温暖", "想你",
    "offer", "dream", "录取", "通过", "中了",
)

LONGING_WORDS = (
    "想你", "想念", "好久不见", "好久没聊", "有点想你", "好想你",
)


def is_longing_utterance(text: str) -> bool:
    """依恋/想念口语，区别于纯开心报喜。"""
    return contains_any(text, LONGING_WORDS)


def is_positive_utterance(text: str) -> bool:
    if is_longing_utterance(text):
        return False
    if contains_any(text, ("不开心", "不高兴", "不喜欢", "不幸福")):
        return False
    return contains_any(text, POSITIVE_WORDS)


def user_complains_bot_reply(text: str) -> bool:
    """用户在纠正 NPC 接话方式（应先安慰、别回忆/别跑题）。"""
    t = text.strip()
    if any(w in t for w in ("答非所问", "乱回", "已读乱回", "接错", "说啥呢", "胡言乱语")):
        return True
    if "不是应该" in t and any(w in t for w in ("安慰", "先陪", "接住")):
        return True
    if "为什么" in t and any(w in t for w in ("回忆", "提这些", "说这些", "记这些", "聊这些")):
        return True
    if any(w in t for w in ("应该先安慰", "首先安慰", "先安慰我", "先安慰")):
        return True
    if "没" in t and "安慰" in t and any(w in t for w in ("为什么", "怎么", "不")):
        return True
    return False
