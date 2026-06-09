"""关系健康度与 LLM 关系归纳。"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass

from ..domain import Persona, Relationship
from ..llm.base import LLMProvider


@dataclass
class RelationshipInsight:
    health_score: float   # 0~100
    summary: str
    trend: str            # warming | stable | cooling | new


def compute_health_score(
    affinity: float,
    sentiment_ema: float,
    interaction_count: int,
) -> float:
    """规则化关系健康度（不依赖 LLM）。"""
    aff_part = affinity * 0.45
    mood_part = (50.0 + sentiment_ema * 50.0) * 0.35
    bond_part = min(25.0, interaction_count * 0.8)
    return max(0.0, min(100.0, aff_part + mood_part + bond_part))


def infer_trend(sentiment_ema: float, last_sentiment: float) -> str:
    if sentiment_ema > 0.15 and last_sentiment >= 0:
        return "warming"
    if sentiment_ema < -0.2 or last_sentiment < -0.4:
        return "cooling"
    if abs(sentiment_ema) < 0.05:
        return "new"
    return "stable"


def rule_summary(rel: Relationship, health: float, trend: str, persona: Persona) -> str:
    stage_cn = {"stranger": "刚认识", "acquainted": "逐渐熟悉", "friend": "像朋友一样", "close": "很亲密"}
    stage = stage_cn.get(rel.stage.value, "刚认识")
    trend_cn = {"warming": "互动在升温", "stable": "关系比较稳定", "cooling": "最近有些低落", "new": "还在互相了解"}
    return f"我和你的关系{stage}，亲密度 {rel.affinity:.0f}/100，{trend_cn.get(trend, '')}。"


def summarize_with_llm(
    llm: LLMProvider,
    persona: Persona,
    rel: Relationship,
    health: float,
    trend: str,
    memories: list[str],
    recent_user_lines: list[str],
) -> str:
    mem_block = "\n".join(f"- {m}" for m in memories[:6]) or "（暂无）"
    user_block = "\n".join(f"- {u}" for u in recent_user_lines[-5:]) or "（暂无）"
    system = (
        f"你是{persona.name}。根据已知事实，用1-2句中文归纳「我和用户的关系与近况」。"
        "禁止编造用户没说过的事。面向未成年人，保持温暖克制。"
    )
    user_msg = (
        f"亲密度:{rel.affinity:.0f}/100 阶段:{rel.stage.value} 健康度:{health:.0f} 趋势:{trend}\n"
        f"记忆:\n{mem_block}\n最近用户说:\n{user_block}"
    )
    try:
        raw = llm.generate(system, [{"role": "user", "content": user_msg}], temperature=0.5)
        text = raw.strip().split("\n")[0][:120]
        return text if len(text) >= 6 else rule_summary(rel, health, trend, persona)
    except Exception:
        return rule_summary(rel, health, trend, persona)


def build_insight(
    llm: LLMProvider | None,
    persona: Persona,
    rel: Relationship,
    sentiment_ema: float,
    last_sentiment: float,
    interaction_count: int,
    memories: list[str],
    recent_user_lines: list[str],
    use_llm: bool = True,
) -> RelationshipInsight:
    health = compute_health_score(rel.affinity, sentiment_ema, interaction_count)
    trend = infer_trend(sentiment_ema, last_sentiment)
    if use_llm and llm is not None and llm.name != "mock":
        summary = summarize_with_llm(
            llm, persona, rel, health, trend, memories, recent_user_lines
        )
    else:
        summary = rule_summary(rel, health, trend, persona)
    return RelationshipInsight(health_score=health, summary=summary, trend=trend)
