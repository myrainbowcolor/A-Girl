"""用户行为、意图、说话方式与思想模式分析，驱动个性化主动沟通。"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, replace

from .domain import EmotionState, Persona, Relationship, UserMeta
from .llm.base import LLMProvider

# 意图关键词
_INTENT_VENT = ("烦", "累", "难过", "压力", "哭", "不想", "崩溃", "委屈", "焦虑", "抑郁", "绝望")
_INTENT_COMFORT = ("孤独", "害怕", "没人", "理解", "陪", "想你了", "寂寞", "孤单")
_INTENT_SHARE = ("开心", "高兴", "成功", "考上", "通过了", "棒", "太好了", "分享", "激动")
_INTENT_ASK = ("吗", "?", "？", "怎么", "为什么", "能不能", "可不可以", "如何", "啥")

# 说话方式
_PARTICLE = ("嗯", "啊", "呀", "吧", "呢", "哈", "哟", "嘛", "噢", "哦", "诶", "哇", "欸")
_RATIONAL = ("因为", "所以", "如果", "但是", "分析", "觉得", "可能", "应该", "逻辑", "原因", "其实")
_VALIDATION = ("你觉得", "是不是", "对吧", "同意", "怎么看", "合理吗", "正常吗", "对吗")
_AVOID = ("随便", "算了", "不说", "没事", "嗯嗯", "ok", "好的", "算了", "无所谓")
_EMOJI_RE = re.compile(
    r"[\U0001F300-\U0001FAFF\U00002600-\U000027BF]|"
    r"[\(（][^\)）]{1,12}[\)）]"
)

_GENERIC = frozenset({"正常互动", "闲聊", "整体平稳", "尚不明确", ""})


@dataclass
class UserInsightAnalysis:
    """单次分析结果。"""
    behavior: str = "正常互动"
    intent: str = "闲聊"
    state: str = "平稳"
    speaking_style: str = "尚不明确"
    thought_pattern: str = "尚不明确"
    profile_summary: str = ""
    proactive_need: str = "none"  # none|follow_up|comfort|celebrate|reconnect
    topic_hint: str = ""
    confidence: float = 0.5


def _avg_len(lines: list[str]) -> float:
    if not lines:
        return 0.0
    return sum(len(x) for x in lines) / len(lines)


def _has_emoji(text: str) -> bool:
    return bool(_EMOJI_RE.search(text))


def _last_user_question(lines: list[str]) -> str | None:
    for line in reversed(lines[-8:]):
        if any(q in line for q in _INTENT_ASK) or line.strip().endswith(("?", "？")):
            return line.strip()[:80]
    return None


def _question_ratio(lines: list[str]) -> float:
    if not lines:
        return 0.0
    hits = sum(
        1 for line in lines
        if any(q in line for q in _INTENT_ASK) or line.strip().endswith(("?", "？"))
    )
    return hits / len(lines)


def analyze_speaking_style(all_lines: list[str]) -> str:
    """跨轮归纳说话方式。"""
    if not all_lines:
        return "尚不明确"

    avg = _avg_len(all_lines)
    particle_hits = sum(
        sum(1 for p in _PARTICLE if p in line) for line in all_lines
    )
    particle_rate = particle_hits / len(all_lines)
    q_rate = _question_ratio(all_lines)
    emoji_rate = sum(1 for line in all_lines if _has_emoji(line)) / len(all_lines)

    traits: list[str] = []
    if avg < 8:
        traits.append("短句为主、表达简练")
    elif avg > 40:
        traits.append("长段叙述、愿意展开")
    elif avg > 20:
        traits.append("中等篇幅、表达有条理")
    else:
        traits.append("口语化、节奏适中")

    if particle_rate >= 1.2:
        traits.append("语气词较多、偏随意亲近")
    elif particle_rate <= 0.2 and avg > 15:
        traits.append("措辞相对正式")

    if q_rate >= 0.45:
        traits.append("爱提问、互动性强")
    elif q_rate >= 0.2:
        traits.append("偶尔抛问题试探")

    if emoji_rate >= 0.25:
        traits.append("常用表情或颜文字")

    return "，".join(traits[:3])


def analyze_thought_pattern(all_lines: list[str], meta: UserMeta) -> str:
    """跨轮归纳思想/思维倾向。"""
    if not all_lines:
        return "尚不明确"

    blob = " ".join(all_lines)
    avg = _avg_len(all_lines)
    scores = {
        "情绪优先": (
            sum(1 for w in _INTENT_VENT + _INTENT_COMFORT if w in blob) * 2
            + (1 if meta.sentiment_ema <= -0.25 else 0)
        ),
        "理性分析": sum(1 for w in _RATIONAL if w in blob),
        "寻求认同": sum(1 for w in _VALIDATION if w in blob) * 2,
        "回避倾向": sum(1 for w in _AVOID if w in blob) + (2 if avg < 6 else 0),
        "探索好奇": int(_question_ratio(all_lines) * len(all_lines) * 1.5),
    }
    best = max(scores, key=scores.get)
    if scores[best] <= 0:
        if meta.interaction_count >= 5:
            return "随聊随想、尚未形成固定模式"
        return "尚不明确"

    detail = {
        "情绪优先": "先感受后道理，需要被接住",
        "理性分析": "习惯因果推理、先想清楚再说",
        "寻求认同": "在意他人看法，常求确认",
        "回避倾向": "遇深话题易简短带过",
        "探索好奇": "爱追问、思维发散",
    }
    return detail.get(best, best)


def analyze_behavior_patterns(
    all_lines: list[str],
    recent: list[str],
    meta: UserMeta,
) -> str:
    """行为模式：结合近期与全量历史。"""
    n = len(all_lines)
    if n == 0:
        return "正常互动"

    behaviors: list[str] = []
    avg_all = _avg_len(all_lines)
    avg_recent = _avg_len(recent) if recent else avg_all

    if len(recent) >= 3 and all(len(x) < 15 for x in recent[-3:]):
        behaviors.append("近期连发短消息，情绪可能较急")
    elif avg_recent > 35:
        behaviors.append("近期愿意深度表达，信任感在提升")
    elif len(recent) >= 3:
        behaviors.append("近期互动较活跃")

    if n >= 6:
        third = max(1, n // 3)
        early = all_lines[:third]
        late = all_lines[-third:]
        early_avg = _avg_len(early)
        late_avg = _avg_len(late)
        if late_avg > early_avg * 1.4 and late_avg > 18:
            behaviors.append("随对话深入，表达愈来愈详细")
        elif early_avg > 12 and late_avg < early_avg * 0.55:
            behaviors.append("后期回复变短，可能疲劳或想收束")

    if avg_all > 35 and "深度" not in "".join(behaviors):
        behaviors.append("整体愿意深度倾诉")
    if meta.interaction_count >= 10:
        behaviors.append("长期回访、关系在累积")
    elif meta.interaction_count >= 5 and not behaviors:
        behaviors.append("稳定互动、持续交流")

    if not behaviors:
        return "正常互动"
    return "；".join(behaviors[:2])


def build_profile_summary(
    behavior: str,
    speaking_style: str,
    thought_pattern: str,
    intent: str,
    state: str,
    message_count: int,
    interaction_count: int,
) -> str:
    """综合画像：聊够轮次后才有内容。"""
    if message_count < 2 and interaction_count < 3:
        return ""

    parts: list[str] = []
    if speaking_style not in _GENERIC:
        parts.append(f"说话{speaking_style}")
    if thought_pattern not in _GENERIC:
        parts.append(f"思维{thought_pattern}")
    if behavior not in _GENERIC:
        parts.append(behavior)
    if intent not in _GENERIC and state not in _GENERIC:
        parts.append(f"近期{intent}、{state}")
    elif intent not in _GENERIC:
        parts.append(f"近期{intent}")

    if not parts:
        return ""
    text = "；".join(parts[:3])
    return text if text.endswith("。") else text + "。"


def merge_trait(old: str, new: str) -> str:
    """稳定特质：新信息更具体时更新，避免每轮退回泛化文案。"""
    if not old or old in _GENERIC:
        return new
    if not new or new in _GENERIC:
        return old
    if old == new:
        return old
    if old in new:
        return new
    if new in old:
        return old
    return new if len(new) >= len(old) else old


def merge_dynamic(old: str, new: str) -> str:
    """动态字段（意图/状态）：优先最新，但保留非泛化旧值。"""
    if new in _GENERIC and old not in _GENERIC:
        return old
    return new or old


def merge_profile(old: str, new: str) -> str:
    if not new:
        return old
    if not old:
        return new
    if old == new or new in old:
        return old
    if old in new:
        return new
    return new if len(new) > len(old) else old


def apply_cumulative_merge(analysis: UserInsightAnalysis, meta: UserMeta) -> UserInsightAnalysis:
    """与历史洞察合并，多轮对话后画像应越来越具体。"""
    return replace(
        analysis,
        behavior=merge_trait(meta.user_behavior, analysis.behavior),
        intent=merge_dynamic(meta.user_intent, analysis.intent),
        state=merge_dynamic(meta.user_state, analysis.state),
        speaking_style=merge_trait(meta.user_speaking_style, analysis.speaking_style),
        thought_pattern=merge_trait(meta.user_thought_pattern, analysis.thought_pattern),
        profile_summary=merge_profile(meta.user_profile_summary, analysis.profile_summary),
    )


def analyze_rules(
    user_lines: list[str],
    meta: UserMeta,
    emotion: EmotionState,
    relationship: Relationship,
) -> UserInsightAnalysis:
    """规则化分析：行为 + 意图 + 状态 + 说话方式 + 思想模式。"""
    if not user_lines:
        return UserInsightAnalysis()

    all_lines = user_lines
    recent = user_lines[-12:]
    ema = meta.sentiment_ema

    behavior = analyze_behavior_patterns(all_lines, recent, meta)
    speaking_style = analyze_speaking_style(all_lines)
    thought_pattern = analyze_thought_pattern(all_lines, meta)

    text_blob = " ".join(recent)
    if any(w in text_blob for w in _INTENT_VENT):
        intent = "倾诉/发泄"
    elif any(w in text_blob for w in _INTENT_COMFORT):
        intent = "寻求陪伴"
    elif any(w in text_blob for w in _INTENT_SHARE):
        intent = "分享喜悦"
    elif _last_user_question(recent):
        intent = "提问/求回应"
    elif thought_pattern.startswith("探索"):
        intent = "好奇探索"
    elif thought_pattern.startswith("寻求"):
        intent = "求确认/求建议"
    else:
        intent = "闲聊"

    if ema <= -0.35 or meta.last_sentiment <= -0.45:
        state = "低落，需要被看见"
    elif ema >= 0.35 and meta.last_sentiment >= 0.3:
        state = "心情不错"
    elif emotion.pleasure <= -0.25:
        state = "有些疲惫或不安"
    elif emotion.arousal >= 0.5:
        state = "情绪偏激动"
    elif len(all_lines) >= 5 and ema > 0.1:
        state = "逐渐放松、愿意聊"
    else:
        state = "整体平稳"

    last = recent[-1]
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

    confidence = 0.4
    if len(all_lines) >= 3:
        confidence += 0.12
    if len(all_lines) >= 8:
        confidence += 0.12
    if meta.interaction_count >= 5:
        confidence += 0.1
    if speaking_style not in _GENERIC:
        confidence += 0.08
    if thought_pattern not in _GENERIC:
        confidence += 0.08
    if proactive_need != "none":
        confidence += 0.1
    if abs(ema) > 0.3:
        confidence += 0.08

    profile_summary = build_profile_summary(
        behavior, speaking_style, thought_pattern, intent, state,
        len(all_lines), meta.interaction_count,
    )

    return UserInsightAnalysis(
        behavior=behavior,
        intent=intent,
        state=state,
        speaking_style=speaking_style,
        thought_pattern=thought_pattern,
        profile_summary=profile_summary,
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
    """LLM 深描（JSON），失败则回退规则结果。"""
    sample = user_lines[-24:] or user_lines
    lines = "\n".join(f"- {u}" for u in sample) or "（无）"
    system = (
        f"你是{persona.name}的用户理解模块。根据多轮对话与数据，输出一行 JSON："
        '{"behavior":"8字内行为模式","intent":"6字内当前意图","state":"8字内当前状态",'
        '"speaking_style":"12字内说话方式","thought_pattern":"12字内思想倾向",'
        '"profile_summary":"30字内综合画像",'
        '"proactive_need":"none|follow_up|comfort|celebrate|reconnect",'
        '"topic_hint":"10字内跟进话题","confidence":0到1的小数}'
        "禁止编造用户没说过的事。画像要具体，避免「正常互动」「闲聊」等空泛词。"
    )
    user = (
        f"互动{meta.interaction_count}轮 亲密度{relationship.affinity:.0f} "
        f"情感EMA{meta.sentiment_ema:.2f}\n用户历史发言({len(user_lines)}条):\n{lines}\n"
        f"规则猜测: 行为={rule_hint.behavior} 意图={rule_hint.intent} "
        f"说话={rule_hint.speaking_style} 思维={rule_hint.thought_pattern}"
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
            behavior=str(data.get("behavior", rule_hint.behavior))[:24],
            intent=str(data.get("intent", rule_hint.intent))[:12],
            state=str(data.get("state", rule_hint.state))[:24],
            speaking_style=str(data.get("speaking_style", rule_hint.speaking_style))[:40],
            thought_pattern=str(data.get("thought_pattern", rule_hint.thought_pattern))[:40],
            profile_summary=str(data.get("profile_summary", rule_hint.profile_summary))[:120],
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
        merged = analyze_with_llm(llm, persona, user_lines, meta, relationship, rule)
        return apply_cumulative_merge(merged, meta)
    return apply_cumulative_merge(rule, meta)


_NEED_CN = {
    "follow_up": "跟进用户未充分回应的话题",
    "comfort": "用户情绪偏低，需主动关怀",
    "celebrate": "用户有好消息，可主动祝贺",
    "reconnect": "关系已建立，适合主动续聊",
}


def meta_to_insight_dict(meta: UserMeta) -> dict[str, str] | None:
    """将 UserMeta 转为 API/流式事件用的洞察字典。"""
    has_data = (
        meta.last_insight_at > 0
        or meta.user_behavior
        or meta.user_speaking_style
        or meta.user_thought_pattern
    )
    if not has_data:
        return None
    return {
        "behavior": meta.user_behavior or "正常互动",
        "intent": meta.user_intent or "闲聊",
        "state": meta.user_state or "平稳",
        "speaking_style": meta.user_speaking_style or "尚不明确",
        "thought_pattern": meta.user_thought_pattern or "尚不明确",
        "profile_summary": meta.user_profile_summary or "",
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
        f"状态:{analysis.state} 说话方式:{analysis.speaking_style} "
        f"思想倾向:{analysis.thought_pattern} 话题线索:{analysis.topic_hint} "
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
