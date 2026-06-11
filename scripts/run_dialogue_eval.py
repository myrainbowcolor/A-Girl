#!/usr/bin/env python3
"""运行对话拟真度场景评测并生成失败报告。

用法:
  python3 scripts/run_dialogue_eval.py
  python3 scripts/run_dialogue_eval.py --report backend/tests/reports/dialogue_quality_report.json

退出码: 0=全部通过, 1=存在失败场景
"""
from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BACKEND = ROOT / "backend"
sys.path.insert(0, str(BACKEND))

from app.config import Settings
from app.db import Database
from app.emotion import EmotionEngine
from app.eval.runner import DialogueScenarioRunner
from app.eval.scenario import load_scenarios
from app.llm import MockLLMProvider
from app.memory import HashEmbeddingProvider, MemoryStore
from app.orchestrator import Orchestrator


def main() -> int:
    parser = argparse.ArgumentParser(description="A-Girl 对话拟真度场景评测")
    parser.add_argument(
        "--scenarios",
        default=str(BACKEND / "tests" / "fixtures" / "dialogue_scenarios"),
        help="场景 JSON 目录",
    )
    parser.add_argument(
        "--report",
        default=str(BACKEND / "tests" / "reports" / "dialogue_quality_report.json"),
        help="输出报告路径",
    )
    args = parser.parse_args()

    scenarios = load_scenarios(args.scenarios)
    if not scenarios:
        print(f"未找到场景文件: {args.scenarios}", file=sys.stderr)
        return 2

    with tempfile.NamedTemporaryFile(suffix=".db") as f:
        settings = Settings(db_path=f.name, reflection_every_n_memories=99)
        db = Database(f.name)
        mem = MemoryStore(db, HashEmbeddingProvider(dim=256), settings)
        orch = Orchestrator(db, mem, EmotionEngine(), MockLLMProvider(), settings)
        runner = DialogueScenarioRunner(orch)
        report = runner.run_all(scenarios, provider="mock")
        db.close()

    report.write_json(args.report)
    print(f"评测完成: {report.passed}/{report.total_scenarios} 通过")
    print(f"报告已写入: {args.report}")

    if report.failures:
        print("\n--- 失败场景（供开发跟进）---")
        seen: set[str] = set()
        for fail in report.failures:
            if fail.scenario_id in seen:
                continue
            seen.add(fail.scenario_id)
            print(f"\n[{fail.scenario_id}] {fail.scenario_name}")
            print(f"  标签: {', '.join(fail.tags)}")
            print(f"  用户: {fail.user_message}")
            print(f"  回复: {fail.agent_reply[:100]}...")
            for issue in fail.issues[:3]:
                print(f"  - {issue['criterion']}: {issue['detail']}")
            if fail.developer_notes:
                print(f"  备注: {fail.developer_notes}")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
