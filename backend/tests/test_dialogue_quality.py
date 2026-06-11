"""对话拟真度场景测试：覆盖场景、背景、心态、情绪、关系与对话时长。

失败用例会写入 backend/tests/reports/dialogue_quality_report.json，
供开发人员定位与修复。
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

import tempfile

from app.config import Settings
from app.db import Database
from app.emotion import EmotionEngine
from app.eval.runner import DialogueScenarioRunner
from app.eval.scenario import load_scenarios
from app.llm import MockLLMProvider
from app.memory import HashEmbeddingProvider, MemoryStore
from app.orchestrator import Orchestrator

SCENARIO_DIR = Path(__file__).resolve().parent / "fixtures" / "dialogue_scenarios"
REPORT_DIR = Path(__file__).resolve().parent / "reports"

ALL_SCENARIOS = load_scenarios(SCENARIO_DIR)
SCENARIO_IDS = [s.id for s in ALL_SCENARIOS]


def _format_failure(sr, failure) -> str:
    lines = [
        f"\n场景: {failure.scenario_name} ({failure.scenario_id})",
        f"标签: {', '.join(failure.tags)}",
        f"轮次: {failure.turn_index}/{failure.total_turns}",
        f"用户: {failure.user_message}",
        f"回复: {failure.agent_reply}",
        f"得分: {failure.score}/100",
    ]
    for issue in failure.issues:
        lines.append(f"  - [{issue['severity']}] {issue['criterion']}: {issue['detail']}")
    if failure.developer_notes:
        lines.append(f"开发备注: {failure.developer_notes}")
    return "\n".join(lines)


@pytest.fixture(scope="module", autouse=True)
def write_dialogue_report(request):
    """测试结束后写出完整评测报告（含失败详情）。"""
    yield
    report_path = REPORT_DIR / "dialogue_quality_report.json"
    cache = getattr(request.config, "_dialogue_eval_cache", None)
    if cache:
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(
            json.dumps(cache, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )


@pytest.fixture(scope="module")
def dialogue_orch():
    with tempfile.NamedTemporaryFile(suffix=".db") as f:
        s = Settings(db_path=f.name, reflection_every_n_memories=99)
        db = Database(f.name)
        mem = MemoryStore(db, HashEmbeddingProvider(dim=256), s)
        o = Orchestrator(db, mem, EmotionEngine(), MockLLMProvider(), s)
        yield o
        db.close()


@pytest.fixture(scope="module")
def full_eval_report(dialogue_orch):
    runner = DialogueScenarioRunner(dialogue_orch)
    return runner.run_all(ALL_SCENARIOS, provider="mock")


def pytest_configure(config):
    config._dialogue_eval_cache = None


@pytest.mark.parametrize("scenario_id", SCENARIO_IDS)
def test_dialogue_scenario(scenario_id, full_eval_report, request):
    """逐场景断言；失败时输出可交给开发同学的结构化信息。"""
    sr = next(r for r in full_eval_report.scenario_results if r.scenario_id == scenario_id)
    request.config._dialogue_eval_cache = full_eval_report.to_dict()

    if sr.passed:
        return

    details = "\n".join(_format_failure(sr, f) for f in sr.failures)
    pytest.fail(f"对话质量未达标:{details}")


def test_dialogue_eval_summary(full_eval_report, request):
    """汇总通过率并确保报告已生成（失败详情见 report JSON 与各场景测试）。"""
    request.config._dialogue_eval_cache = full_eval_report.to_dict()
    assert full_eval_report.total_scenarios >= 1
    # 失败场景由 test_dialogue_scenario 逐项断言；此处仅记录汇总供报告使用
    assert full_eval_report.passed + full_eval_report.failed == full_eval_report.total_scenarios
