"""对话质量场景执行器。"""
from __future__ import annotations

import tempfile
import time
from dataclasses import dataclass, field

from ..config import Settings
from ..db import Database
from ..domain import Relationship
from ..emotion import EmotionEngine
from ..llm import LLMProvider, MockLLMProvider
from ..memory import HashEmbeddingProvider, MemoryStore
from ..orchestrator import Orchestrator
from .evaluator import DialogueEvaluator, QualityIssue, TurnContext
from .scenarios import DialogueScenario


@dataclass
class TurnRecord:
    turn_index: int
    user_text: str
    reply: str
    llm: str
    avatar_expression: str
    avatar_animation: str
    affinity: float
    relationship_stage: str
    retrieved_memories: list[str] = field(default_factory=list)


@dataclass
class ScenarioResult:
    scenario: DialogueScenario
    passed: bool
    score: float
    issues: list[QualityIssue] = field(default_factory=list)
    turns: list[TurnRecord] = field(default_factory=list)

    @property
    def critical_issues(self) -> list[QualityIssue]:
        return [i for i in self.issues if i.severity == "critical"]

    @property
    def major_issues(self) -> list[QualityIssue]:
        return [i for i in self.issues if i.severity == "major"]


class DialogueQualityRunner:
    def __init__(
        self,
        llm: LLMProvider | None = None,
        settings: Settings | None = None,
        evaluator: DialogueEvaluator | None = None,
    ) -> None:
        self._llm = llm or MockLLMProvider()
        self._settings = settings or Settings(reflection_every_n_memories=999)
        self._evaluator = evaluator or DialogueEvaluator()

    def run_scenario(self, scenario: DialogueScenario) -> ScenarioResult:
        with tempfile.NamedTemporaryFile(suffix=".db") as f:
            db = Database(f.name)
            mem = MemoryStore(db, HashEmbeddingProvider(dim=256), self._settings)
            orch = Orchestrator(
                db, mem, EmotionEngine(), self._llm, self._settings
            )
            user_id = f"dq-{scenario.id}"
            session_id = f"sess-{scenario.id}"

            rel = Relationship(affinity=scenario.initial_affinity)
            rel.recompute_stage()
            db.save_relationship(user_id, rel, time.time())

            for seed in scenario.seed_memories:
                mem.add(user_id, seed, importance=5.0)

            turn_contexts: list[TurnContext] = []
            turn_records: list[TurnRecord] = []
            prior_user: list[str] = []
            all_issues: list[QualityIssue] = []

            for idx, spec in enumerate(scenario.turns):
                result = orch.chat(user_id, session_id, spec.user)
                ctx = TurnContext(
                    turn_index=idx,
                    user_text=spec.user,
                    result=result,
                    prior_user_texts=list(prior_user),
                    retrieved_memories=list(result.retrieved_memories),
                )
                all_issues.extend(
                    self._evaluator.evaluate_turn(
                        ctx,
                        expect_empathy=spec.expect_empathy,
                        expect_warmth=spec.expect_warmth,
                        forbid_intimate_tone=spec.forbid_intimate_tone,
                        expect_comfort_avatar=spec.expect_comfort_avatar,
                        expect_recall=spec.expect_recall,
                        recall_keywords=spec.recall_keywords,
                    )
                )
                turn_contexts.append(ctx)
                turn_records.append(
                    TurnRecord(
                        turn_index=idx,
                        user_text=spec.user,
                        reply=result.reply,
                        llm=result.llm,
                        avatar_expression=result.avatar.expression if result.avatar else "",
                        avatar_animation=result.avatar.animation if result.avatar else "",
                        affinity=result.relationship.affinity,
                        relationship_stage=result.relationship.stage.value,
                        retrieved_memories=list(result.retrieved_memories),
                    )
                )
                prior_user.append(spec.user)

            all_issues.extend(
                self._evaluator.evaluate_session(
                    turn_contexts,
                    scenario.expectation,
                    initial_affinity=scenario.initial_affinity,
                )
            )

            seen: set[tuple[str, int | None, str]] = set()
            unique_issues: list[QualityIssue] = []
            for issue in all_issues:
                key = (issue.rule_id, issue.turn_index, issue.message)
                if key not in seen:
                    seen.add(key)
                    unique_issues.append(issue)

            score = self._evaluator.score(unique_issues)
            passed = not any(i.severity == "critical" for i in unique_issues)

            db.close()
            return ScenarioResult(
                scenario=scenario,
                passed=passed,
                score=score,
                issues=unique_issues,
                turns=turn_records,
            )

    def run_all(self, scenarios: list[DialogueScenario]) -> list[ScenarioResult]:
        return [self.run_scenario(s) for s in scenarios]
