"""对话拟真度场景测试：多维度用例 + 主动沟通 + 失败记录。"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.dialogue_quality import (
    DialogueQualityReporter,
    DialogueQualityRunner,
    all_proactive_scenarios,
    all_scenarios,
)
from app.llm import MockLLMProvider

_REPORT_DIR = Path(__file__).resolve().parent.parent / "reports" / "dialogue_quality"


@pytest.fixture(scope="module")
def dialogue_results():
    runner = DialogueQualityRunner(llm=MockLLMProvider())
    dialogue = runner.run_all(all_scenarios())
    proactive = runner.run_all_proactive(all_proactive_scenarios())
    results = dialogue + proactive
    DialogueQualityReporter(_REPORT_DIR).write_run_report(results, llm_name="mock")
    return results


def _result_for(results, scenario_id: str):
    return next(r for r in results if r.scenario.id == scenario_id)


@pytest.mark.parametrize("scenario", all_scenarios(), ids=lambda s: s.id)
def test_dialogue_scenario_no_critical_issues(scenario, dialogue_results):
    """每个对话场景不得出现 critical 级质量问题（安全/机械腔/空回复等）。"""
    result = _result_for(dialogue_results, scenario.id)
    critical = result.critical_issues
    assert not critical, (
        f"场景 {scenario.id} 存在 critical 问题："
        + "; ".join(f"{i.rule_id}: {i.message}" for i in critical)
    )


@pytest.mark.parametrize("scenario", all_scenarios(), ids=lambda s: s.id)
def test_dialogue_scenario_no_major_issues(scenario, dialogue_results):
    """mock 基线下每个对话场景也不应出现 major 级拟真度问题。"""
    result = _result_for(dialogue_results, scenario.id)
    major = result.major_issues
    assert not major, (
        f"场景 {scenario.id} 存在 major 问题："
        + "; ".join(f"{i.rule_id}: {i.message}" for i in major)
    )


@pytest.mark.parametrize("scenario", all_proactive_scenarios(), ids=lambda s: s.id)
def test_proactive_scenario_no_critical_issues(scenario, dialogue_results):
    """主动沟通场景不得出现 critical 级问题。"""
    result = _result_for(dialogue_results, scenario.id)
    critical = result.critical_issues
    assert not critical, (
        f"主动场景 {scenario.id} 存在 critical 问题："
        + "; ".join(f"{i.rule_id}: {i.message}" for i in critical)
    )


@pytest.mark.parametrize("scenario", all_proactive_scenarios(), ids=lambda s: s.id)
def test_proactive_scenario_no_major_issues(scenario, dialogue_results):
    """主动沟通场景不应出现 major 级拟真度问题。"""
    result = _result_for(dialogue_results, scenario.id)
    major = result.major_issues
    assert not major, (
        f"主动场景 {scenario.id} 存在 major 问题："
        + "; ".join(f"{i.rule_id}: {i.message}" for i in major)
    )


def test_dialogue_quality_report_written(dialogue_results):
    latest = _REPORT_DIR / "latest.json"
    assert latest.exists()
    data = json.loads(latest.read_text(encoding="utf-8"))
    expected_total = len(all_scenarios()) + len(all_proactive_scenarios())
    assert data["summary"]["total_scenarios"] == expected_total
    assert "failures" in data


def test_dialogue_quality_summary(dialogue_results):
    """整体平均分应维持在可接受区间（mock LLM 基线）。"""
    avg = sum(r.score for r in dialogue_results) / len(dialogue_results)
    assert avg >= 70.0, f"整体平均分过低：{avg:.1f}"
