"""对话拟真度场景测试：多维度用例 + 失败记录。"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.dialogue_quality import (
    DialogueQualityReporter,
    DialogueQualityRunner,
    all_scenarios,
)
from app.llm import MockLLMProvider

_REPORT_DIR = Path(__file__).resolve().parent.parent / "reports" / "dialogue_quality"


@pytest.fixture(scope="module")
def dialogue_results():
    runner = DialogueQualityRunner(llm=MockLLMProvider())
    results = runner.run_all(all_scenarios())
    DialogueQualityReporter(_REPORT_DIR).write_run_report(results, llm_name="mock")
    return results


@pytest.mark.parametrize("scenario", all_scenarios(), ids=lambda s: s.id)
def test_dialogue_scenario_no_critical_issues(scenario, dialogue_results):
    """每个场景不得出现 critical 级质量问题（安全/机械腔/空回复等）。"""
    result = next(r for r in dialogue_results if r.scenario.id == scenario.id)
    critical = result.critical_issues
    assert not critical, (
        f"场景 {scenario.id} 存在 critical 问题："
        + "; ".join(f"{i.rule_id}: {i.message}" for i in critical)
    )


@pytest.mark.parametrize("scenario", all_scenarios(), ids=lambda s: s.id)
def test_dialogue_scenario_no_major_issues(scenario, dialogue_results):
    """mock 基线下每个场景也不应出现 major 级拟真度问题。"""
    result = next(r for r in dialogue_results if r.scenario.id == scenario.id)
    major = result.major_issues
    assert not major, (
        f"场景 {scenario.id} 存在 major 问题："
        + "; ".join(f"{i.rule_id}: {i.message}" for i in major)
    )


def test_dialogue_quality_report_written(dialogue_results):
    latest = _REPORT_DIR / "latest.json"
    assert latest.exists()
    data = json.loads(latest.read_text(encoding="utf-8"))
    assert data["summary"]["total_scenarios"] == len(all_scenarios())
    assert "failures" in data


def test_dialogue_quality_summary(dialogue_results):
    """整体平均分应维持在可接受区间（mock LLM 基线）。"""
    avg = sum(r.score for r in dialogue_results) / len(dialogue_results)
    assert avg >= 70.0, f"整体平均分过低：{avg:.1f}"


def test_memory_format_leak_detection():
    """记忆存储格式不应出现在用户可见回复中。"""
    from app.avatar import AvatarCue
    from app.dialogue_quality.evaluator import DialogueEvaluator, TurnContext
    from app.domain import EmotionState, Relationship
    from app.orchestrator import ChatResult

    ev = DialogueEvaluator()
    rel = Relationship(affinity=40)
    rel.recompute_stage()
    result = ChatResult(
        reply="当然记得呀，ta 说：我养了一只猫",
        emotion=EmotionState(),
        relationship=rel,
        avatar=AvatarCue(expression="平静", intensity=0.5, animation="idle"),
        retrieved_memories=[],
        is_crisis=False,
        llm="mock",
    )
    ctx = TurnContext(turn_index=0, user_text="你还记得吗", result=result)
    issues = ev.evaluate_turn(ctx)
    assert any(i.rule_id == "memory_format_leak" for i in issues)
