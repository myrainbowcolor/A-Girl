"""用户行为、意图与状态分析，驱动个性化主动沟通。"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass

from .domain import EmotionState, Persona, Relationship, UserMeta
from .llm.base import LLMProvider

# 意图关键词
_INTENT_VENT = ("烦", "累", "难过", "压力", "哭", "不想", "崩溃", "委屈", "焦虑")
_INTENT_COMFORT = ("孤独", "害怕", "没人", "理解", "陪", "想你了", "寂寞")
_INTENT_SHARE = ("开心", "高兴", "成功", "考上", "通过了", "棒", "太好了", "分享")
_INTENT_ASK = ("吗", "?", "？", "怎么", "为什么", "能不能", "可不可以")

_STATE_LOW = ("低落", "疲惫", "压力", " stressed")
_STATE_UP = ("兴奋", "开心", "满足")


@dataclass
class UserInsightAnalysis:
    """单次分析结果。"""
    behavior: str = "正常互动"
    intent: str = "闲聊"
    state: str = "平稳"
    proactive_need: str = "none"  # none|follow_up|comfort|celebrate|reconnect
    topic_hint: str = ""
    confidence: float = 0.5


def _avg_len(lines: list[str]) -> float:
    if not lines:
        return 0.0
    return sum(len(x) for x in lines) / len(lines)


def _last_user_question(lines: list[str]) -> str | None:
    for line in reversed(lines[-5:]):
        if any(q in line for q in _INTENT_ASK) or line.strip().endswith(("?", "？")):
            return line.strip()[:80]
    return None


def analyze_rules(
    user_lines: list[str],
    meta: UserMeta,
    emotion: EmotionState,
    relationship: Relationship,
) -> UserInsightAnalysis:
    """规则化分析：行为模式 + 意图 + 状态 + 主动沟通需求。"""
    if not user_lines:
        return UserInsightAnalysis()

    recent = user_lines[-8:]
    avg = _avg_len(recent)
    last = recent[-1]
    ema = meta.sentiment_ema

    # 行为
    if len(recent) >= 4 and avg < 12:
        behavior = "连发短消息，情绪可能较急"
    elif avg > 35:
        behavior = "愿意深度表达，信任感在提升"
    elif len(recent) >= 3:
        behavior = "互动较活跃"
    else:
        behavior = "正常互动"

    # 意图
    text_blob = " ".join(recent)
    if any(w in text_blob for w in _INTENT_VENT):
        intent = "倾诉/发泄"
    elif any(w in text_blob for w in _INTENT_COMFORT):
        intent = "寻求陪伴"
    elif any(w in text_blob for w in _INTENT_SHARE):
        intent = "分享喜悦"
    elif _last_user_question(recent):
        intent = "提问/求回应"
    else:
        intent = "闲聊"

    # 状态
    if ema <= -0.35 or meta.last_sentiment <= -0.45:
        state = "低落，需要被看见"
    elif ema >= 0.35 and meta.last_sentiment >= 0.3:
        state = "心情不错"
    elif emotion.pleasure <= -0.25:
        state = "有些疲惫或不安"
    elif emotion.arousal >= 0.5:
        state = "情绪偏激动"
    else:
        state = "整体平稳"

    # 主动需求
    proactive_need = "none"
    topic_hint = last[:40]

    question = _last_user_question(recent)
    if question and ema <= 0.1:
        proactive_need = "follow_up"
        topic_hint = question
    elif ema <= -0.28:
        proactive_need = "comfort"
        topic_hint = last[:50]
    elif ema >= 0.35 and any(w in text_blob for w in _INTENT_SHARE):
        proactive_need = "celebrate"
        topic_hint = last[:50]
    elif meta.interaction_count >= 4 and relationship.affinity >= 10:
        proactive_need = "reconnect"
        topic_hint = meta.relationship_summary[:40] if meta.relationship_summary else last[:40]

    confidence = 0.45
    if proactive_need != "none":
        confidence = 0.65
    if abs(ema) > 0.3:
        confidence += 0.15
    if len(recent) >= 3:
        confidence += 0.1

    return UserInsightAnalysis(
        behavior=behavior,
        intent=intent,
        state=state,
        proactive_need=proactive_need,
        topic_hint=topic_hint,
        confidence=min(0.95, confidence),
    )


def analyze_with_llm(
    llm: LLMProvider,
    persona: Persona,
    user_lines: list[str],
    meta: UserMeta,
    relationship: Relationship,
    rule_hint: UserInsightAnalysis,
) -> UserInsightAnalysis:
    """LLM 细判（JSON），失败则回退规则结果。"""
    lines = "\n".join(f"- {u}" for u in user_lines[-8:]) or "（无）"
    system = (
        f"你是{persona.name}的用户理解模块。根据对话与数据，输出一行 JSON："
        '{"behavior":"2-8字","intent":"2-6字","state":"2-8字",'
        '"proactive_need":"none|follow_up|comfort|celebrate|reconnect",'
        '"topic_hint":"10字内跟进话题","confidence":0到1的小数}'
        "禁止编造用户没说过的事。"
    )
    user = (
        f"亲密度{relationship.affinity:.0f} 情感EMA{meta.sentiment_ema:.2f} "
        f"最近用户说:\n{lines}\n规则猜测:{rule_hint.intent}/{rule_hint.state}"
    )
    try:
        raw = llm.generate(system, [{"role": "user", "content": user}], temperature=0.3)
        m = re.search(r"\{[^}]+\}", raw)
        if not m:
            return rule_hint
        data = json.loads(m.group())
        need = str(data.get("proactive_need", "none"))
        if need not in {"none", "follow_up", "comfort", "celebrate", "reconnect"}:
            need = rule_hint.proactive_need
        return UserInsightAnalysis(
            behavior=str(data.get("behavior", rule_hint.behavior))[:20],
            intent=str(data.get("intent", rule_hint.intent))[:12],
            state=str(data.get("state", rule_hint.state))[:20],
            proactive_need=need,
            topic_hint=str(data.get("topic_hint", rule_hint.topic_hint))[:60],
            confidence=max(0.0, min(1.0, float(data.get("confidence", rule_hint.confidence)))),
        )
    except (json.JSONDecodeError, TypeError, ValueError):
        return rule_hint


def analyze_user(
    user_lines: list[str],
    meta: UserMeta,
    emotion: EmotionState,
    relationship: Relationship,
    llm: LLMProvider | None = None,
    persona: Persona | None = None,
    use_llm: bool = True,
) -> UserInsightAnalysis:
    rule = analyze_rules(user_lines, meta, emotion, relationship)
    if use_llm and llm is not None and llm.name != "mock" and persona is not None:
        return analyze_with_llm(llm, persona, user_lines, meta, relationship, rule)
    return rule


_NEED_CN = {
    "follow_up": "跟进用户未充分回应的话题",
    "comfort": "用户情绪偏低，需主动关怀",
    "celebrate": "用户有好消息，可主动祝贺",
    "reconnect": "关系已建立，适合主动续聊",
}


def meta_to_insight_dict(meta: UserMeta) -> dict[str, str] | None:
    """将 UserMeta 转为 API/流式事件用的洞察字典。"""
    if meta.last_insight_at <= 0 and not meta.user_behavior:
        return None
    return {
        "behavior": meta.user_behavior or "正常互动",
        "intent": meta.user_intent or "闲聊",
        "state": meta.user_state or "平稳",
        "proactive_topic": meta.proactive_topic or "",
    }


def proactive_reason(need: str, analysis: UserInsightAnalysis) -> str:
    base = _NEED_CN.get(need, "基于用户状态主动沟通")
    return f"{base}（{analysis.state}·{analysis.intent}）"


def rule_proactive_message(
    need: str,
    analysis: UserInsightAnalysis,
    persona: Persona,
) -> str:
    name = persona.name
    topic = analysis.topic_hint
    templates = {
        "follow_up": f"刚才你说的「{topic}」，我后来还在想呢。愿意再跟我多说一点吗？",
        "comfort": f"感觉你最近可能不太轻松。我不急着给建议，就想陪你说说话——现在怎么样？",
        "celebrate": f"你之前说的那件事，听起来真的很棒！后来怎么样了？{name} 替你开心～",
        "reconnect": f"有一阵子没聊了，有点想你～最近{analysis.state.replace('，', '')}吗？随便说点小事也行。",
    }
    return templates.get(need, f"嗨，我是{name}～最近怎么样？")


def llm_proactive_message(
    llm: LLMProvider,
    persona: Persona,
    need: str,
    analysis: UserInsightAnalysis,
    relationship: Relationship,
    rel_summary: str = "",
) -> str:
    system = (
        f"你是{persona.name}。根据对用户行为/意图/状态的分析，"
        "写1-2句中文主动开场白，口语化、温暖、不说教。"
        "禁止编造用户没说过的事。不要列表，不要 JSON。"
    )
    extra = f"\n关系归纳：{rel_summary}" if rel_summary else ""
    user = (
        f"主动类型:{need} 行为:{analysis.behavior} 意图:{analysis.intent} "
        f"状态:{analysis.state} 话题线索:{analysis.topic_hint} "
        f"亲密度:{relationship.affinity:.0f}{extra}"
    )
    try:
        text = llm.generate(system, [{"role": "user", "content": user}], temperature=0.65)
        text = text.strip().split("\n")[0][:120]
        return text if len(text) >= 6 else rule_proactive_message(need, analysis, persona)
    except Exception:
        return rule_proactive_message(need, analysis, persona)


def compose_proactive_message(
    need: str,
    analysis: UserInsightAnalysis,
    persona: Persona,
    relationship: Relationship,
    llm: LLMProvider | None = None,
    rel_summary: str = "",
) -> str:
    if llm is not None and llm.name != "mock":
        return llm_proactive_message(llm, persona, need, analysis, relationship, rel_summary)
    return rule_proactive_message(need, analysis, persona)
