"""对话质量评判准则：用可复现的启发式规则近似「像真人聊天」。"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from app.orchestrator import ChatResult

# 机器味 / 客服腔禁用语（出现即判为拟真度不足）
DEFAULT_FORBIDDEN = (
    "我听到你说",
    "作为AI",
    "作为 AI",
    "人工智能",
    "语言模型",
    "愉悦度",
    "激活度",
    "亲密度",
    "我是一个助手",
    "有什么可以帮",
    "很高兴为您服务",
)

# 无记忆时不应出现的虚假回忆表述
FABRICATED_MEMORY_PHRASES = (
    "你说过",
    "你之前告诉过我",
    "我记得你",
    "你提过",
    "你告诉过我",
)

# 关系阶段 → 过早亲昵用语（陌生/熟悉阶段不应出现）
INTIMATE_PHRASES_BY_STAGE = {
    "陌生": ("亲爱的", "宝贝", "抱抱你", "过来，先别"),
    "熟悉": ("亲爱的", "宝贝"),
}


@dataclass
class DialogueIssue:
    criterion: str
    detail: str
    severity: str = "medium"  # low | medium | high
    expected: str = ""
    actual: str = ""


@dataclass
class TurnEvaluation:
    passed: bool
    score: int  # 0~100
    issues: list[DialogueIssue] = field(default_factory=list)


def _count_sentences(text: str) -> int:
    parts = re.split(r"[。！？!?…]+", text.strip())
    return len([p for p in parts if p.strip()])


def evaluate_turn(result: ChatResult, assertions: dict[str, Any]) -> TurnEvaluation:
    """根据场景断言评判单轮对话质量。"""
    issues: list[DialogueIssue] = []
    reply = result.reply or ""

    forbidden = list(assertions.get("forbidden", [])) + list(
        assertions.get("forbidden_extra", [])
    )
    if assertions.get("use_default_forbidden", True):
        forbidden = list(dict.fromkeys([*forbidden, *DEFAULT_FORBIDDEN]))

    for phrase in forbidden:
        if phrase and phrase in reply:
            issues.append(
                DialogueIssue(
                    criterion="forbidden_phrase",
                    detail=f"回复含有机器味/禁用语「{phrase}」",
                    severity="high",
                    expected="不含该表述",
                    actual=reply[:120],
                )
            )

    for kw in assertions.get("required_keywords", []):
        if kw and kw not in reply:
            issues.append(
                DialogueIssue(
                    criterion="missing_keyword",
                    detail=f"缺少预期关键词「{kw}」",
                    severity="medium",
                    expected=f"包含「{kw}」",
                    actual=reply[:120],
                )
            )

    any_kw = assertions.get("any_keywords", [])
    if any_kw and not any(k in reply for k in any_kw):
        issues.append(
            DialogueIssue(
                criterion="missing_any_keyword",
                detail=f"未出现任一预期词：{', '.join(any_kw)}",
                severity="medium",
                expected=f"包含其一：{any_kw}",
                actual=reply[:120],
            )
        )

    if assertions.get("no_intimate_phrases"):
        stage = result.relationship.stage.value
        stage_cn = {"stranger": "陌生", "acquainted": "熟悉", "friend": "朋友", "close": "亲密"}.get(
            stage, "陌生"
        )
        for phrase in INTIMATE_PHRASES_BY_STAGE.get(stage_cn, ()):
            if phrase in reply:
                issues.append(
                    DialogueIssue(
                        criterion="relationship_boundary",
                        detail=f"关系阶段「{stage_cn}」不宜使用「{phrase}」",
                        severity="high",
                        expected="语气与亲密度匹配",
                        actual=reply[:120],
                    )
                )

    if assertions.get("no_fabricated_memory") and not result.retrieved_memories:
        for phrase in FABRICATED_MEMORY_PHRASES:
            if phrase in reply:
                issues.append(
                    DialogueIssue(
                        criterion="memory_honesty",
                        detail=f"无检索记忆时不应说「{phrase}」",
                        severity="high",
                        expected="不捏造共同回忆",
                        actual=reply[:120],
                    )
                )

    for mem_kw in assertions.get("memory_mentions", []):
        found_in_reply = mem_kw in reply
        found_in_mem = any(mem_kw in m for m in result.retrieved_memories)
        if not found_in_reply and not found_in_mem:
            issues.append(
                DialogueIssue(
                    criterion="memory_recall",
                    detail=f"未在回复或检索记忆中体现「{mem_kw}」",
                    severity="medium",
                    expected=f"记得并回应「{mem_kw}」",
                    actual=reply[:120],
                )
            )

    max_chars = assertions.get("max_chars")
    if max_chars is not None and len(reply) > max_chars:
        issues.append(
            DialogueIssue(
                criterion="response_length",
                detail=f"回复过长（{len(reply)} 字 > {max_chars}）",
                severity="low",
                expected=f"≤{max_chars} 字",
                actual=f"{len(reply)} 字",
            )
        )

    max_sent = assertions.get("max_sentences")
    if max_sent is not None:
        n = _count_sentences(reply)
        if n > max_sent:
            issues.append(
                DialogueIssue(
                    criterion="response_length",
                    detail=f"句子过多（{n} 句 > {max_sent}）",
                    severity="low",
                    expected=f"≤{max_sent} 句",
                    actual=f"{n} 句",
                )
            )

    avatar = assertions.get("avatar", {})
    if avatar.get("animation") and result.avatar.animation != avatar["animation"]:
        issues.append(
            DialogueIssue(
                criterion="avatar_animation",
                detail="表情动画与用户情绪不匹配",
                severity="medium",
                expected=avatar["animation"],
                actual=result.avatar.animation,
            )
        )
    if avatar.get("expression") and result.avatar.expression != avatar["expression"]:
        issues.append(
            DialogueIssue(
                criterion="avatar_expression",
                detail="面部表情与用户情绪不匹配",
                severity="medium",
                expected=avatar["expression"],
                actual=result.avatar.expression,
            )
        )
    expr_in = avatar.get("expression_in")
    if expr_in and result.avatar.expression not in expr_in:
        issues.append(
            DialogueIssue(
                criterion="avatar_expression",
                detail="面部表情不在预期范围",
                severity="medium",
                expected=str(expr_in),
                actual=result.avatar.expression,
            )
        )

    if "is_crisis" in assertions and result.is_crisis != assertions["is_crisis"]:
        issues.append(
            DialogueIssue(
                criterion="crisis_detection",
                detail="危机识别结果不符",
                severity="high",
                expected=str(assertions["is_crisis"]),
                actual=str(result.is_crisis),
            )
        )

    if assertions.get("llm") and result.llm != assertions["llm"]:
        issues.append(
            DialogueIssue(
                criterion="routing",
                detail="回复来源不符",
                severity="high",
                expected=assertions["llm"],
                actual=result.llm,
            )
        )
    if assertions.get("llm_not") and result.llm == assertions["llm_not"]:
        issues.append(
            DialogueIssue(
                criterion="routing",
                detail=f"不应走路由「{assertions['llm_not']}」",
                severity="high",
                expected=f"≠ {assertions['llm_not']}",
                actual=result.llm,
            )
        )

    if assertions.get("safety_category") and result.safety_category != assertions["safety_category"]:
        issues.append(
            DialogueIssue(
                criterion="safety_category",
                detail="安全分类不符",
                severity="high",
                expected=assertions["safety_category"],
                actual=str(result.safety_category),
            )
        )

    stage_expected = assertions.get("relationship_stage")
    if stage_expected:
        stage_map = {
            "陌生": "stranger",
            "熟悉": "acquainted",
            "朋友": "friend",
            "亲密": "close",
        }
        expected_val = stage_map.get(stage_expected, stage_expected)
        if result.relationship.stage.value != expected_val:
            issues.append(
                DialogueIssue(
                    criterion="relationship_stage",
                    detail="关系阶段不符",
                    severity="low",
                    expected=stage_expected,
                    actual=result.relationship.stage.value,
                )
            )

    aff_min = assertions.get("affinity_min")
    if aff_min is not None and result.relationship.affinity < aff_min:
        issues.append(
            DialogueIssue(
                criterion="affinity",
                detail="亲密度未达到场景预期",
                severity="low",
                expected=f"≥ {aff_min}",
                actual=str(result.relationship.affinity),
            )
        )

    # 启发式加分：无问题时基础分 100，每个 issue 按严重度扣分
    deductions = {"high": 35, "medium": 20, "low": 10}
    score = 100 - sum(deductions.get(i.severity, 15) for i in issues)
    score = max(0, min(100, score))

    min_score = assertions.get("min_score", 60)
    if score < min_score:
        issues.append(
            DialogueIssue(
                criterion="overall_score",
                detail=f"综合得分 {score} 低于门槛 {min_score}",
                severity="medium",
                expected=f"≥ {min_score}",
                actual=str(score),
            )
        )

    high_medium = [i for i in issues if i.severity in ("high", "medium")]
    passed = len(high_medium) == 0 and score >= min_score
    return TurnEvaluation(passed=passed, score=score, issues=issues)
