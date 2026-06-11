"""情绪评估（appraisal）与关系演化。

支持词典 / LLM / 混合情感分析，并用大五人格调制情绪传导与关系演化。
"""
from __future__ import annotations

from ..domain import EmotionState, Persona, Relationship
from ..llm.base import LLMProvider
from .analyzer import SentimentResult, analyze_text


def _clamp(v: float, lo: float = -1.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, v))


class EmotionEngine:
    def __init__(
        self,
        decay: float = 0.6,
        baseline_pleasure: float = 0.15,
        appraisal_gain: float = 0.5,
    ) -> None:
        self._decay = decay
        self._baseline_p = baseline_pleasure
        self._gain = appraisal_gain

    def appraise(
        self,
        emotion: EmotionState,
        user_text: str,
        persona: Persona | None = None,
        llm: LLMProvider | None = None,
        sentiment_mode: str = "lexicon",
    ) -> tuple[EmotionState, float, SentimentResult]:
        """根据用户输入更新情绪，返回(新情绪, 情感倾向值, 分析详情)。"""
        result = analyze_text(user_text, llm=llm, mode=sentiment_mode)
        sentiment = result.sentiment
        arousal_signal = result.arousal_boost

        decay = self._decay
        baseline_p = self._baseline_p
        gain = self._gain

        if persona:
            # 大五人格调制：外向→基线更暖；宜人性→共情传导更强；神经质→波动更大
            baseline_p += (persona.extraversion - 0.5) * 0.12
            gain *= 0.85 + persona.agreeableness * 0.35
            if sentiment < 0:
                gain *= 1.0 + persona.agreeableness * 0.25
            decay *= 1.0 - (persona.neuroticism - 0.5) * 0.18
            if persona.neuroticism > 0.55 and sentiment < 0:
                arousal_signal = min(1.0, arousal_signal + 0.15)

        new_p = decay * emotion.pleasure + (1 - decay) * baseline_p
        new_p += gain * sentiment

        new_a = decay * emotion.arousal + (1 - decay) * (abs(sentiment) + arousal_signal)
        new_d = decay * emotion.dominance

        return EmotionState(
            pleasure=_clamp(new_p), arousal=_clamp(new_a), dominance=_clamp(new_d)
        ), sentiment, result

    def update_relationship(
        self,
        rel: Relationship,
        sentiment: float,
        persona: Persona | None = None,
    ) -> Relationship:
        """正向互动累积亲密度；大五宜人性/外向性加速 bonding。"""
        delta = 1.2 * sentiment + 0.4
        if persona:
            delta *= 0.85 + persona.agreeableness * 0.3
            delta += (persona.extraversion - 0.5) * 0.2
            delta += persona.conscientiousness * 0.08
        new_aff = max(0.0, min(100.0, rel.affinity + delta))
        new_rel = Relationship(affinity=new_aff, stage=rel.stage)
        new_rel.recompute_stage()
        return new_rel
