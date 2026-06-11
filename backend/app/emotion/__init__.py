"""情感与关系子系统。"""
from .analyzer import SentimentResult, analyze_lexicon, analyze_text
from .engine import EmotionEngine


def analyze_sentiment(text: str) -> float:
    """返回 [-1, 1] 的情感倾向（兼容旧接口）。"""
    return analyze_lexicon(text).sentiment


__all__ = ["EmotionEngine", "analyze_sentiment", "SentimentResult", "analyze_text"]
