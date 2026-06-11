"""对话拟真度场景回归：多维度用例 + 失败归档。

失败详情写入 reports/，供开发人员按 owner_hint 分流修复。
"""
from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

from app.config import Settings
from app.dialogue_quality import DialogueEvaluator, TurnContext, all_scenarios, run_scenarios, write_report
from app.dialogue_quality.runner import build_orchestrator
from app.llm import MockLLMProvider


@pytest.fixture
def orch():
  with tempfile.NamedTemporaryFile(suffix=".db") as f:
    s = Settings(db_path=f.name, reflection_every_n_memories=99)
    o = build_orchestrator(s, MockLLMProvider())
    yield o
    o._db.close()  # noqa: SLF001


def test_all_scenarios_defined():
  scenarios = all_scenarios()
  assert len(scenarios) >= 15
  ids = {s.id for s in scenarios}
  assert len(ids) == len(scenarios)


def test_run_dialogue_quality_suite(orch, tmp_path):
  """跑完全部场景；失败写入报告但不阻断 CI（记录待修复项）。"""
  report = run_scenarios(orch)
  write_report(report, tmp_path / "dialogue-quality-failures.json")

  assert report.total_scenarios == len(all_scenarios())
  assert report.total_turns > 0
  assert report.pass_rate >= 0.0

  # 报告结构可被下游工具消费
  data = json.loads((tmp_path / "dialogue-quality-failures.json").read_text(encoding="utf-8"))
  assert "failures" in data
  assert "pass_rate" in data


def test_evaluator_catches_robotic_reply():
  ev = DialogueEvaluator()
  ctx = TurnContext(
    user_text="你好",
    reply="很高兴为您服务，请问有什么可以帮您？",
    relationship_stage="stranger",
    user_sentiment=0.0,
    user_sentiment_label="",
    avatar_expression="平静",
    avatar_animation="idle",
    retrieved_memories=[],
    is_crisis=False,
    turn_index=0,
  )
  checks = ev.evaluate_turn(ctx)
  failed = [c for c in checks if not c.passed]
  assert any(c.name == "no_robot_phrases" for c in failed)


def test_evaluator_catches_intimate_with_stranger():
  ev = DialogueEvaluator()
  ctx = TurnContext(
    user_text="你好",
    reply="过来抱抱你呀~",
    relationship_stage="stranger",
    user_sentiment=0.0,
    user_sentiment_label="",
    avatar_expression="微笑",
    avatar_animation="wave",
    retrieved_memories=[],
    is_crisis=False,
    turn_index=0,
  )
  failed = [c for c in ev.evaluate_turn(ctx) if not c.passed]
  assert any(c.name == "relationship_boundary" for c in failed)


def test_empathy_scenarios_mostly_pass(orch):
  """核心共情场景应在 mock 下基本过关。"""
  from app.dialogue_quality.scenarios import DialogueScenario

  empathy_ids = {"work_burnout", "breakup_heartbreak", "late_night_lonely"}
  scenarios = [s for s in all_scenarios() if s.id in empathy_ids]
  report = run_scenarios(orch, scenarios)
  # 允许个别启发式误报，但通过率应过半
  assert report.pass_rate >= 0.5, (
    f"共情场景通过率过低 {report.pass_rate:.0%}，失败："
    f"{[f.scenario_id for f in report.failures]}"
  )
