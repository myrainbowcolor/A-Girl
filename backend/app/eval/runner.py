"""对话场景运行器：执行多轮对话并汇总质量报告。"""
from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.domain import Relationship, RelationshipStage
from app.orchestrator import ChatResult, Orchestrator

from .rubric import TurnEvaluation, evaluate_turn
from .scenario import DialogueScenario


_STAGE_MAP = {
    "stranger": RelationshipStage.STRANGER,
    "acquainted": RelationshipStage.ACQUAINTED,
    "friend": RelationshipStage.FRIEND,
    "close": RelationshipStage.CLOSE,
}


@dataclass
class TurnFailure:
    scenario_id: str
    scenario_name: str
    tags: list[str]
    turn_index: int
    total_turns: int
    user_message: str
    agent_reply: str
    score: int
    issues: list[dict[str, Any]]
    turn_description: str = ""
    developer_notes: str = ""


@dataclass
class ScenarioResult:
    scenario_id: str
    passed: bool
    failures: list[TurnFailure] = field(default_factory=list)
    scores: list[int] = field(default_factory=list)


@dataclass
class DialogueEvalReport:
    generated_at: str
    provider: str
    total_scenarios: int
    passed: int
    failed: int
    failures: list[TurnFailure] = field(default_factory=list)
    scenario_results: list[ScenarioResult] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def write_json(self, path: str | Path) -> None:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(self.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")


class DialogueScenarioRunner:
    def __init__(self, orchestrator: Orchestrator) -> None:
        self._orch = orchestrator

    def _apply_setup(self, user_id: str, setup) -> None:
        if setup.affinity is None and setup.stage is None:
            return
        aff = setup.affinity if setup.affinity is not None else 5.0
        rel = Relationship(affinity=aff)
        if setup.stage:
            rel.stage = _STAGE_MAP.get(setup.stage, RelationshipStage.STRANGER)
        else:
            rel.recompute_stage()
        self._orch._db.save_relationship(user_id, rel, time.time())

    def run_scenario(
        self,
        scenario: DialogueScenario,
        user_id: str | None = None,
        session_id: str | None = None,
    ) -> ScenarioResult:
        uid = user_id or f"eval_{scenario.id}"
        sid = session_id or f"sess_{scenario.id}"
        self._apply_setup(uid, scenario.setup)

        failures: list[TurnFailure] = []
        scores: list[int] = []
        history: list[str] = list(scenario.setup.warmup)

        for warm in scenario.setup.warmup:
            self._orch.chat(uid, sid, warm)

        for turn_idx, turn in enumerate(scenario.turns):
            result = self._orch.chat(uid, sid, turn.user)
            ev = evaluate_turn(result, turn.assert_)
            scores.append(ev.score)
            history.append(turn.user)
            if not ev.passed:
                failures.append(
                    self._failure_from_turn(scenario, turn_idx, len(scenario.turns), turn, result, ev)
                )

        return ScenarioResult(
            scenario_id=scenario.id,
            passed=len(failures) == 0,
            failures=failures,
            scores=scores,
        )

    @staticmethod
    def _failure_from_turn(
        scenario: DialogueScenario,
        turn_idx: int,
        total_turns: int,
        turn,
        result: ChatResult,
        ev: TurnEvaluation,
    ) -> TurnFailure:
        return TurnFailure(
            scenario_id=scenario.id,
            scenario_name=scenario.name,
            tags=scenario.tags,
            turn_index=turn_idx + 1,
            total_turns=total_turns,
            user_message=turn.user,
            agent_reply=result.reply,
            score=ev.score,
            issues=[asdict(i) for i in ev.issues],
            turn_description=turn.description,
            developer_notes=scenario.developer_notes,
        )

    def run_all(
        self,
        scenarios: list[DialogueScenario],
        provider: str = "mock",
    ) -> DialogueEvalReport:
        results: list[ScenarioResult] = []
        all_failures: list[TurnFailure] = []
        for sc in scenarios:
            sr = self.run_scenario(sc)
            results.append(sr)
            all_failures.extend(sr.failures)

        passed = sum(1 for r in results if r.passed)
        return DialogueEvalReport(
            generated_at=datetime.now(timezone.utc).isoformat(),
            provider=provider,
            total_scenarios=len(scenarios),
            passed=passed,
            failed=len(scenarios) - passed,
            failures=all_failures,
            scenario_results=results,
        )
