"""情绪评估（appraisal）与关系演化。

骨架阶段用轻量词典做情感倾向分析，驱动 PAD 情绪更新与关系亲密度变化；
生产期可替换为模型化的情感分析，接口保持不变。
"""
from __future__ import annotations

from ..domain import EmotionState, Relationship

# 轻量中文情感词典（骨架用，可替换为模型）
_POSITIVE = {
    "喜欢", "开心", "高兴", "爱", "谢谢", "感谢", "想你", "想念", "好棒", "厉害",
    "温暖", "幸福", "哈哈", "棒", "可爱", "陪", "在乎", "甜", "笑", "感动",
    "安心", "放松", "治愈", "满足", "期待", "顺利", "抱抱",
}
_NEGATIVE = {
    "难过", "伤心", "累", "烦", "讨厌", "孤独", "痛苦", "失望", "生气", "委屈",
    "压力", "焦虑", "崩溃", "哭", "无聊", "糟糕", "不开心", "想哭", "绝望",
    "郁闷", "无助", "迷茫", "失眠", "害怕", "担心", "烦死了", "撑不住",
}
_HIGH_AROUSAL = {"兴奋", "激动", "生气", "崩溃", "焦虑", "愤怒", "害怕", "惊喜", "紧张", "慌"}


def analyze_sentiment(text: str) -> float:
    """返回 [-1, 1] 的情感倾向。"""
    pos = sum(1 for w in _POSITIVE if w in text)
    neg = sum(1 for w in _NEGATIVE if w in text)
    total = pos + neg
    if total == 0:
        return 0.0
    return max(-1.0, min(1.0, (pos - neg) / total))


def _clamp(v: float, lo: float = -1.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, v))


class EmotionEngine:
    def __init__(
        self,
        decay: float = 0.6,           # 情绪向基线回落系数（越大越"稳"）
        baseline_pleasure: float = 0.15,
        appraisal_gain: float = 0.5,  # 用户情绪对 NPC 情绪的传导强度
    ) -> None:
        self._decay = decay
        self._baseline_p = baseline_pleasure
        self._gain = appraisal_gain

    def appraise(self, emotion: EmotionState, user_text: str) -> tuple[EmotionState, float]:
        """根据用户输入更新情绪，返回(新情绪, 情感倾向值)。"""
        sentiment = analyze_sentiment(user_text)
        arousal_signal = 0.5 if any(w in user_text for w in _HIGH_AROUSAL) else 0.0

        # 愉悦度：先向基线回落，再叠加本轮情感传导
        new_p = self._decay * emotion.pleasure + (1 - self._decay) * self._baseline_p
        new_p += self._gain * sentiment

        # 激活度：情绪强度越大（无论正负）越高，强情绪词额外加成
        new_a = self._decay * emotion.arousal + (1 - self._decay) * (abs(sentiment) + arousal_signal)

        # 支配度：暂随时间回落到中性
        new_d = self._decay * emotion.dominance

        return EmotionState(
            pleasure=_clamp(new_p), arousal=_clamp(new_a), dominance=_clamp(new_d)
        ), sentiment

    def update_relationship(self, rel: Relationship, sentiment: float) -> Relationship:
        """正向互动累积亲密度，负向小幅消耗；亲密度变化是慢变量。"""
        delta = 1.2 * sentiment + 0.4  # 每轮基础正向 +0.4，模拟"陪伴本身在加深关系"
        new_aff = max(0.0, min(100.0, rel.affinity + delta))
        new_rel = Relationship(affinity=new_aff, stage=rel.stage)
        new_rel.recompute_stage()
        return new_rel
