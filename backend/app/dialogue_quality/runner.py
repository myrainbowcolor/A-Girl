"""对话质量场景执行器。"""
from __future__ import annotations

import tempfile
import time
from dataclasses import dataclass, field

from ..config import Settings
from ..db import Database
from ..domain import Event, Message, Persona, Relationship, UserMeta
from ..emotion import EmotionEngine
from ..llm import LLMProvider, MockLLMProvider
from ..memory import HashEmbeddingProvider, MemoryStore
from ..orchestrator import Orchestrator
from ..proactivity import ProactivityEngine
from .evaluator import DialogueEvaluator, QualityIssue, TurnContext
from .proactive_scenarios import ProactiveScenario
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
class ProactiveRecord:
    trigger: str
    reason: str
    message: str
    proactive_need: str | None = None


@dataclass
class ScenarioResult:
    scenario: DialogueScenario | ProactiveScenario
    passed: bool
    score: float
    issues: list[QualityIssue] = field(default_factory=list)
    turns: list[TurnRecord] = field(default_factory=list)
    proactive: ProactiveRecord | None = None
    scenario_kind: str = "dialogue"

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
                scenario_kind="dialogue",
            )

    def run_all(self, scenarios: list[DialogueScenario]) -> list[ScenarioResult]:
        return [self.run_scenario(s) for s in scenarios]

    def run_proactive_scenario(self, scenario: ProactiveScenario) -> ScenarioResult:
        setup = scenario.setup
        now = time.time()
        with tempfile.NamedTemporaryFile(suffix=".db") as f:
            settings = Settings(
                db_path=f.name,
                reflection_every_n_memories=999,
                proactive_idle_seconds=6 * 3600,
                proactive_insight_enabled=True,
                proactive_insight_min_idle_seconds=1800,
                proactive_insight_cooldown_seconds=3600,
                proactive_insight_min_confidence=0.55,
                user_insight_use_llm=False,
                proactive_event_window_seconds=86400,
            )
            db = Database(f.name)
            persona = Persona()
            engine = ProactivityEngine(db, settings, persona, self._llm)
            user_id = f"dq-p-{scenario.id}"
            session_id = f"sess-{user_id}"

            rel = Relationship(affinity=setup.initial_affinity)
            rel.recompute_stage()
            db.save_relationship(user_id, rel, now)

            if not setup.no_history:
                base_ts = now - setup.last_interaction_idle_seconds - 60
                for idx, text in enumerate(setup.user_messages):
                    db.add_message(
                        Message(
                            session_id=session_id,
                            role="user",
                            content=text,
                            created_at=base_ts + idx,
                        )
                    )
                db.save_user_meta(
                    UserMeta(
                        user_id=user_id,
                        last_interaction_at=now - setup.last_interaction_idle_seconds,
                        last_sentiment=setup.last_sentiment,
                        sentiment_ema=setup.sentiment_ema,
                        interaction_count=setup.interaction_count,
                        last_proactive_at=now - setup.last_proactive_idle_seconds,
                    )
                )

            for ev in setup.events:
                db.add_event(
                    Event(
                        user_id=user_id,
                        kind=ev.kind,
                        label=ev.label,
                        trigger_at=now + ev.trigger_offset_seconds,
                        created_at=now - 86400,
                    )
                )

            result = engine.check(user_id, now=now)
            message = result.message or ""
            issues = self._evaluator.evaluate_proactive(
                message,
                expected_trigger=scenario.expected_trigger,
                actual_trigger=result.trigger or "",
                expected_need=scenario.expected_need,
                actual_need=result.insight.proactive_need if result.insight else None,
                expect_empathy=scenario.expect_empathy,
                expect_warmth=scenario.expect_warmth,
                forbid_intimate_tone=scenario.forbid_intimate_tone,
            )

            if not result.should_reach_out:
                issues.insert(
                    0,
                    QualityIssue(
                        "proactive_not_triggered",
                        "critical",
                        f"场景应触发主动沟通（期望 {scenario.expected_trigger}）",
                    ),
                )

            score = self._evaluator.score(issues)
            passed = not any(i.severity == "critical" for i in issues)
            db.close()
            return ScenarioResult(
                scenario=scenario,
                passed=passed,
                score=score,
                issues=issues,
                proactive=ProactiveRecord(
                    trigger=result.trigger or "",
                    reason=result.reason or "",
                    message=message,
                    proactive_need=result.insight.proactive_need if result.insight else None,
                ),
                scenario_kind="proactive",
            )

    def run_all_proactive(self, scenarios: list[ProactiveScenario]) -> list[ScenarioResult]:
        return [self.run_proactive_scenario(s) for s in scenarios]
