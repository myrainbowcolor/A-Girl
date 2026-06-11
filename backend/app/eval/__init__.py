"""对话拟真度评测：场景用例、质量准则与运行器。"""
from .rubric import DialogueIssue, TurnEvaluation, evaluate_turn
from .runner import DialogueEvalReport, DialogueScenarioRunner
from .scenario import DialogueScenario, load_scenarios

__all__ = [
    "DialogueIssue",
    "TurnEvaluation",
    "evaluate_turn",
    "DialogueEvalReport",
    "DialogueScenarioRunner",
    "DialogueScenario",
    "load_scenarios",
]
