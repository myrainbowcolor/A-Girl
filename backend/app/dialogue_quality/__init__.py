"""对话拟真度质量评估：场景用例、规则打分与失败记录。"""
from .evaluator import DialogueEvaluator, QualityCheck, TurnContext
from .reporter import FailureRecord, QualityReport, write_report
from .runner import run_scenarios
from .scenarios import DialogueScenario, all_scenarios

__all__ = [
    "DialogueEvaluator",
    "DialogueScenario",
    "FailureRecord",
    "QualityCheck",
    "QualityReport",
    "TurnContext",
    "all_scenarios",
    "run_scenarios",
    "write_report",
]
