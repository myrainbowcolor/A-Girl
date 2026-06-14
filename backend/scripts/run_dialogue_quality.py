#!/usr/bin/env python3
"""运行对话质量评测并输出失败记录。

用法：
  cd backend
  python scripts/run_dialogue_quality.py
  python scripts/run_dialogue_quality.py --strict   # 有问题时 exit 1
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.dialogue_quality import (
    DialogueQualityReporter,
    DialogueQualityRunner,
    all_scenarios,
    filter_scenarios,
)
from app.llm import MockLLMProvider


def main() -> int:
    parser = argparse.ArgumentParser(description="A-Girl 对话拟真度质量评测")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="存在 critical/major 问题时返回非零退出码",
    )
    parser.add_argument(
        "--scenario",
        action="append",
        dest="scenario_ids",
        help="仅运行指定场景 id，可重复传入",
    )
    parser.add_argument("--relationship", help="按关系维度筛选（子串匹配）")
    parser.add_argument("--emotion", help="按情绪维度筛选（子串匹配）")
    parser.add_argument("--duration", help="按对话时长筛选（子串匹配）")
    parser.add_argument("--scene", help="按场景维度筛选（子串匹配）")
    args = parser.parse_args()

    scenarios = filter_scenarios(
        relationship=args.relationship,
        emotion=args.emotion,
        duration=args.duration,
        scene=args.scene,
    )
    if args.scenario_ids:
        wanted = set(args.scenario_ids)
        scenarios = [s for s in scenarios if s.id in wanted]
        missing = wanted - {s.id for s in scenarios}
        if missing:
            print(f"未找到场景：{', '.join(sorted(missing))}", file=sys.stderr)
            return 2

    llm = MockLLMProvider()
    runner = DialogueQualityRunner(llm=llm)
    results = runner.run_all(scenarios)
    report_path = DialogueQualityReporter().write_run_report(results, llm_name=llm.name)

    summary = DialogueQualityReporter()._summary(results)
    print(
        f"评测完成：{summary['total_scenarios']} 场景"
        f"（基线 {summary['baseline_scenarios']} + 扩展 {summary['extended_scenarios']}），"
        f"{summary['scenarios_with_issues']} 个有问题"
        f"（基线 {summary['baseline_with_issues']} / 扩展 {summary['extended_with_issues']}），"
        f"平均分 {summary['average_score']}（基线 {summary['baseline_average_score']}）"
    )
    print(f"报告：{report_path}")
    print(f"Markdown：{report_path.parent / 'latest.md'}")
    print(f"失败流水：{report_path.parent / 'failures.jsonl'}")

    for r in results:
        if not r.issues:
            continue
        print(f"\n[{r.scenario.id}] {r.scenario.name} — 得分 {r.score}")
        for issue in r.issues:
            turn = f" turn={issue.turn_index}" if issue.turn_index is not None else ""
            print(f"  - {issue.severity} {issue.rule_id}{turn}: {issue.message}")

    if args.strict:
        baseline = [r for r in results if r.scenario.baseline]
        if any(r.critical_issues or r.major_issues for r in baseline):
            return 1
    elif any(r.critical_issues for r in results):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
