"""对话拟真度质量评测：场景用例、启发式评分与失败记录。"""
from .evaluator import DialogueEvaluator, QualityIssue, TurnContext
from .proactive_scenarios import (
    ProactiveScenario,
    all_proactive_scenarios,
    filter_proactive_scenarios,
)
from .reporter import DialogueQualityReporter
from .runner import DialogueQualityRunner, ScenarioResult
from .scenarios import DialogueScenario, all_scenarios, filter_scenarios, scenarios_by_dimension

__all__ = [
    "DialogueEvaluator",
    "DialogueQualityReporter",
    "DialogueQualityRunner",
    "DialogueScenario",
    "ProactiveScenario",
    "QualityIssue",
    "ScenarioResult",
    "TurnContext",
    "all_proactive_scenarios",
    "all_scenarios",
    "filter_proactive_scenarios",
    "filter_scenarios",
    "scenarios_by_dimension",
]
