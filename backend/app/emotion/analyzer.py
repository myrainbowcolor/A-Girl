"""用户消息情感分析：词典 + 可选 LLM 增强。"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass

from ..llm.base import LLMProvider

_POSITIVE = {
    "喜欢", "开心", "高兴", "爱", "谢谢", "感谢", "想你", "想念", "好棒", "厉害",
    "温暖", "幸福", "哈哈", "棒", "可爱", "陪", "在乎", "甜", "笑",
    "怀念",  # 怀旧回忆：暖而柔软，驱动柔和微笑而非呆板平静脸
}
_NEGATIVE = {
    "难过", "伤心", "累", "烦", "讨厌", "孤独", "痛苦", "失望", "生气", "委屈",
    "压力", "焦虑", "崩溃", "哭", "糟糕", "不开心", "想哭", "绝望",
    # 倾诉/不适类：影响 user_sentiment → 数字人安抚表情
    "紧张", "记不住", "难受", "落寞", "想家", "孤单", "头痛", "头疼", "感冒",
    "生病", "不舒服", "差劲", "害怕", "很怕", "失眠", "撑不住", "空落落",
    # 育儿焦虑 / 自责（不含单字「怕」，避免「别怕」误判）
    "考不好", "太严厉", "严厉", "耽误",
    # 自我怀疑 / 低落口语（不含「无聊」——闲聊无聊≠情绪危机）
    "原地踏步", "踏步", "emo", "丧", "心累", "没用", "自卑", "迷茫", "憋着", "自我怀疑",
    # 失恋 / 异地 / 疲惫口语（不含单字「好难」——避免怀旧「难静下来」误判）
    "分手", "失恋", "异地", "好空", "困死", "空落落",
}
_HIGH_AROUSAL = {
    "兴奋", "激动", "生气", "烦", "崩溃", "焦虑", "愤怒", "害怕", "惊喜", "委屈",
    "紧张", "失眠",
}
_INTENSITY = {"非常", "特别", "超级", "极其", "太", "好", "很", "超"}
# 强喜悦词：怀旧场景不含这些时，正向强度应克制
_STRONG_JOY = {"开心", "高兴", "哈哈", "棒", "好棒", "太棒", "幸福", "喜欢", "录取", "通过", "offer"}


@dataclass
class SentimentResult:
    """用户本轮情感分析结果。"""
    sentiment: float = 0.0       # [-1, 1]
    arousal_boost: float = 0.0 # [0, 1] 额外激活度
    label: str = "中性"
    source: str = "lexicon"


def analyze_lexicon(text: str) -> SentimentResult:
    pos = sum(1 for w in _POSITIVE if w in text)
    neg = sum(1 for w in _NEGATIVE if w in text)
    total = pos + neg
    sentiment = 0.0 if total == 0 else max(-1.0, min(1.0, (pos - neg) / total))
    # 怀旧偏正向：柔和微笑即可，避免当成「超开心」大笑
    if "怀念" in text and sentiment > 0 and neg == 0 and not any(w in text for w in _STRONG_JOY):
        sentiment = min(sentiment, 0.42)
    arousal = 0.5 if any(w in text for w in _HIGH_AROUSAL) else 0.0
    if any(w in text for w in _INTENSITY):
        arousal = min(1.0, arousal + 0.25)
    if sentiment > 0.3:
        label = "偏正向"
    elif sentiment < -0.3:
        label = "偏负向"
    else:
        label = "中性"
    return SentimentResult(sentiment, arousal, label, "lexicon")


def analyze_with_llm(llm: LLMProvider, text: str) -> SentimentResult:
    """用 LLM 做细粒度情感分析（JSON）。"""
    system = (
        "你是情感分析组件。只输出一行 JSON，不要其它文字。"
        '格式：{"sentiment":-1到1的小数,"arousal":0到1的小数,"label":"2-6字中文情绪词"}'
    )
    try:
        raw = llm.generate(system, [{"role": "user", "content": text}], temperature=0.2)
        m = re.search(r"\{[^}]+\}", raw)
        if not m:
            return analyze_lexicon(text)
        data = json.loads(m.group())
        return SentimentResult(
            sentiment=max(-1.0, min(1.0, float(data.get("sentiment", 0)))),
            arousal_boost=max(0.0, min(1.0, float(data.get("arousal", 0)))),
            label=str(data.get("label", "中性"))[:12],
            source="llm",
        )
    except (json.JSONDecodeError, TypeError, ValueError):
        return analyze_lexicon(text)


def analyze_text(
    text: str,
    llm: LLMProvider | None = None,
    mode: str = "lexicon",
) -> SentimentResult:
    """mode: lexicon | llm | hybrid（先词典，中性且 LLM 可用时再调 LLM）。"""
    lex = analyze_lexicon(text)
    if mode == "lexicon" or llm is None:
        return lex
    if mode == "llm":
        return analyze_with_llm(llm, text)
    # hybrid
    if abs(lex.sentiment) < 0.15 and lex.arousal_boost < 0.2:
        return analyze_with_llm(llm, text)
    return lex
