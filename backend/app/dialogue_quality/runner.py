"""执行场景用例并汇总质量报告。"""
from __future__ import annotations

import time
from pathlib import Path

from ..config import Settings
from ..db import Database
from ..domain import Relationship, RelationshipStage
from ..emotion import EmotionEngine
from ..llm import LLMProvider, MockLLMProvider
from ..memory import HashEmbeddingProvider, MemoryStore
from ..orchestrator import Orchestrator
from .evaluator import DialogueEvaluator, TurnContext
from .reporter import FailureRecord, QualityReport, build_summary, utc_now_iso, write_markdown_summary, write_report
from .scenarios import DialogueScenario, all_scenarios

_STAGE_AFFINITY = {
  "stranger": (5.0, RelationshipStage.STRANGER),
  "acquainted": (25.0, RelationshipStage.ACQUAINTED),
  "friend": (50.0, RelationshipStage.FRIEND),
  "close": (75.0, RelationshipStage.CLOSE),
}


def _seed_relationship(db: Database, user_id: str, relationship: str) -> None:
  aff, stage = _STAGE_AFFINITY.get(relationship, (5.0, RelationshipStage.STRANGER))
  db.save_relationship(user_id, Relationship(affinity=aff, stage=stage), time.time())


def run_scenarios(
  orchestrator: Orchestrator,
  scenarios: list[DialogueScenario] | None = None,
  *,
  evaluator: DialogueEvaluator | None = None,
) -> QualityReport:
  scenarios = scenarios or all_scenarios()
  ev = evaluator or DialogueEvaluator()
  llm_name = orchestrator._llm.name  # noqa: SLF001 — 测试运行器需记录 provider

  failures: list[FailureRecord] = []
  total_turns = 0
  passed_turns = 0

  for sc in scenarios:
    user_id = f"dq-{sc.id}"
    session_id = f"sess-{sc.id}"
    _seed_relationship(orchestrator._db, user_id, sc.relationship)  # noqa: SLF001
    prior_user: list[str] = []

    for turn_idx, user_text in enumerate(sc.user_turns):
      result = orchestrator.chat(user_id, session_id, user_text)
      total_turns += 1
      rel_stage = result.relationship.stage.value

      ctx = TurnContext(
        user_text=user_text,
        reply=result.reply,
        relationship_stage=rel_stage,
        user_sentiment=_sentiment_from_label(result.user_sentiment_label, user_text),
        user_sentiment_label=result.user_sentiment_label,
        avatar_expression=result.avatar.expression,
        avatar_animation=result.avatar.animation,
        retrieved_memories=result.retrieved_memories,
        is_crisis=result.is_crisis,
        turn_index=turn_idx,
        prior_user_texts=list(prior_user),
      )
      checks = ev.evaluate_turn(ctx)
      failed = [c for c in checks if not c.passed]

      if failed:
        failures.append(
          FailureRecord(
            scenario_id=sc.id,
            scenario_title=sc.title,
            scene=sc.scene,
            background=sc.background,
            mindset=sc.mindset,
            emotion=sc.emotion,
            relationship=sc.relationship,
            duration=sc.duration,
            turn_index=turn_idx,
            user_text=user_text,
            reply=result.reply,
            failed_checks=[
              {
                "name": c.name,
                "severity": c.severity,
                "message": c.message,
                "owner_hint": c.owner_hint,
              }
              for c in failed
            ],
            tags=sc.tags,
            notes=sc.notes,
            llm_provider=llm_name,
          )
        )
      else:
        passed_turns += 1

      prior_user.append(user_text)

  return QualityReport(
    generated_at=utc_now_iso(),
    llm_provider=llm_name,
    total_scenarios=len(scenarios),
    total_turns=total_turns,
    passed_turns=passed_turns,
    failed_turns=len(failures),
    failures=failures,
    summary_by_owner=build_summary(failures),
  )


def _sentiment_from_label(label: str, user_text: str) -> float:
  """从标签或关键词粗估 sentiment，供评估器使用。"""
  if any(w in label for w in ("负面", "低落", "焦虑", "委屈")):
    return -0.6
  if any(w in label for w in ("开心", "兴奋", "正面")):
    return 0.6
  neg_kw = ("难过", "烦", "累", "焦虑", "哭", "分手", "孤独", "压力", "无聊", "麻木")
  pos_kw = ("开心", "哈哈", "谢谢", "offer", "温暖", "好玩")
  if any(k in user_text for k in neg_kw):
    return -0.5
  if any(k in user_text for k in pos_kw):
    return 0.5
  return 0.0


def build_orchestrator(settings: Settings | None = None, llm: LLMProvider | None = None) -> Orchestrator:
  s = settings or Settings(db_path=":memory:")
  db = Database(s.db_path)
  mem = MemoryStore(db, HashEmbeddingProvider(dim=s.embedding_dim), s)
  return Orchestrator(db, mem, EmotionEngine(), llm or MockLLMProvider(), s)


def run_and_write_reports(
  out_dir: Path | str = "reports",
  settings: Settings | None = None,
  llm: LLMProvider | None = None,
) -> QualityReport:
  out = Path(out_dir)
  orch = build_orchestrator(settings, llm)
  report = run_scenarios(orch)
  write_report(report, out / "dialogue-quality-failures.json")
  write_markdown_summary(report, out / "dialogue-quality-report.md")
  return report
