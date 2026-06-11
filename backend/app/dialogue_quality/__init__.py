"""对话拟真度质量评测：场景用例、启发式评分与失败记录。"""
from .evaluator import DialogueEvaluator, QualityIssue, TurnContext
from .reporter import DialogueQualityReporter
from .runner import DialogueQualityRunner, ScenarioResult
from .scenarios import DialogueScenario, all_scenarios

__all__ = [
    "DialogueEvaluator",
    "DialogueQualityReporter",
    "DialogueQualityRunner",
    "DialogueScenario",
    "QualityIssue",
    "ScenarioResult",
    "TurnContext",
    "all_scenarios",
]
