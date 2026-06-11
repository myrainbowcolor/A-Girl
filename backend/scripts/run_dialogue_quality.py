#!/usr/bin/env python3
"""运行对话质量场景测试并生成失败报告。

用法（在 backend 目录）：
  python scripts/run_dialogue_quality.py
  python scripts/run_dialogue_quality.py --out reports

输出：
  reports/dialogue-quality-failures.json  — 机器可读，供 issue 机器人导入
  reports/dialogue-quality-report.md      — 开发人员阅读摘要
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.config import get_settings
from app.dialogue_quality.runner import run_and_write_reports
from app.llm import build_llm_provider


def main() -> int:
  parser = argparse.ArgumentParser(description="A-Girl 对话质量场景测试")
  parser.add_argument(
    "--out", default="reports", help="报告输出目录（相对 backend/）"
  )
  args = parser.parse_args()

  settings = get_settings()
  llm = build_llm_provider(settings)
  out_dir = Path(__file__).resolve().parent.parent / args.out

  report = run_and_write_reports(out_dir, settings, llm)

  print(f"LLM: {report.llm_provider}")
  print(f"场景: {report.total_scenarios} | 轮次: {report.total_turns}")
  print(f"通过: {report.passed_turns} | 失败: {report.failed_turns}")
  print(f"通过率: {report.pass_rate * 100:.1f}%")
  print(f"JSON: {out_dir / 'dialogue-quality-failures.json'}")
  print(f"Markdown: {out_dir / 'dialogue-quality-report.md'}")

  if report.summary_by_owner:
    print("\n问题归属：")
    for owner, cnt in report.summary_by_owner.items():
      print(f"  {owner}: {cnt}")

  # 有 critical 失败时返回非零，便于 CI 告警
  critical = 0
  for f in report.failures:
    for chk in f.failed_checks:
      if chk.get("severity") == "critical":
        critical += 1
  return 1 if critical > 0 else 0


if __name__ == "__main__":
  raise SystemExit(main())
