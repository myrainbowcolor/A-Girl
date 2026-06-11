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


def test_dimension_coverage():
    """六维场景库应覆盖主要关系阶段与时长档位。"""
    scenarios = all_scenarios()
    relationships = {s.relationship for s in scenarios}
    durations = {s.duration for s in scenarios}
    assert "陌生" in relationships
    assert "朋友" in relationships
    assert "亲密" in relationships
    assert any("单轮" in d for d in durations)
    assert any("6轮" in d for d in durations)
    assert len(scenarios) >= 26


def test_failure_recording(tmp_path):
    """质量不达标时应写入 failures.jsonl 供开发跟进。"""
    from app.dialogue_quality.evaluator import QualityIssue
    from app.dialogue_quality.runner import ScenarioResult, TurnRecord
    from app.dialogue_quality.scenarios import all_scenarios

    scenario = all_scenarios()[0]
    result = ScenarioResult(
        scenario=scenario,
        passed=False,
        score=40.0,
        issues=[
            QualityIssue("missing_empathy", "major", "测试用失败记录", 0),
        ],
        turns=[
            TurnRecord(
                turn_index=0,
                user_text="测试",
                reply="机械回复",
                llm="mock",
                avatar_expression="平静",
                avatar_animation="idle",
                affinity=5.0,
                relationship_stage="stranger",
            )
        ],
    )
    report_dir = tmp_path / "dialogue_quality"
    DialogueQualityReporter(report_dir).write_run_report([result], llm_name="test")

    failures = (report_dir / "failures.jsonl").read_text(encoding="utf-8").strip()
    assert failures
    row = json.loads(failures.splitlines()[-1])
    assert row["scenario_id"] == scenario.id
    assert row["issues"][0]["fix_hint"]
    assert row["transcript"]
