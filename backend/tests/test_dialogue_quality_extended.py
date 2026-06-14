"""扩展对话拟真度场景：记录失败供开发人员修复，不阻塞基线 CI。

基线 CI 仅跑 test_dialogue_quality.py；本文件用于扩展场景集的质量探测。
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.dialogue_quality import (
    DialogueQualityReporter,
    DialogueQualityRunner,
    extended_scenarios,
)
from app.llm import MockLLMProvider

_REPORT_DIR = Path(__file__).resolve().parent.parent / "reports" / "dialogue_quality"


@pytest.fixture(scope="module")
def extended_results():
    runner = DialogueQualityRunner(llm=MockLLMProvider())
    results = runner.run_all(extended_scenarios())
    DialogueQualityReporter(_REPORT_DIR).write_run_report(
        results, llm_name="mock", suite="extended"
    )
    return results


@pytest.mark.parametrize("scenario", extended_scenarios(), ids=lambda s: s.id)
def test_extended_scenario_records_quality_issues(scenario, extended_results):
    """扩展场景：有问题时记录到 failures.jsonl，并以 xfail 标记待修复项。"""
    result = next(r for r in extended_results if r.scenario.id == scenario.id)
    if not result.issues:
        return
    detail = "; ".join(f"{i.rule_id}: {i.message}" for i in result.issues)
    pytest.xfail(f"拟真度待改进 — {detail}")


def test_extended_quality_report_written(extended_results):
    latest = _REPORT_DIR / "extended_latest.json"
    assert latest.exists()
    data = json.loads(latest.read_text(encoding="utf-8"))
    assert data["suite"] == "extended"
    assert data["summary"]["total_scenarios"] == len(extended_scenarios())
