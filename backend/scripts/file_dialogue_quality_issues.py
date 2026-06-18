#!/usr/bin/env python3
"""从对话质量报告创建 GitHub Issue（测试 Automation 用，不开 PR）。

用法：
  cd backend
  python scripts/file_dialogue_quality_issues.py --dry-run
  python scripts/file_dialogue_quality_issues.py --merged-pr 42
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

REPORT = Path(__file__).resolve().parent.parent / "reports" / "dialogue_quality" / "latest.json"
LABEL = "dialogue-quality"


def _load_failures(path: Path) -> tuple[dict, list[dict]]:
    if not path.is_file():
        print(f"报告不存在：{path}，请先运行 run_dialogue_quality.py", file=sys.stderr)
        raise SystemExit(2)
    data = json.loads(path.read_text(encoding="utf-8"))
    failures = data.get("failures") or []
    # 只上报 critical / major
    filtered: list[dict] = []
    for f in failures:
        issues = [
            i
            for i in f.get("issues", [])
            if i.get("severity") in ("critical", "major")
        ]
        if issues:
            copy = dict(f)
            copy["issues"] = issues
            filtered.append(copy)
    return data, filtered


def _group_by_rule(failures: list[dict]) -> dict[str, list[dict]]:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for f in failures:
        for issue in f.get("issues", []):
            grouped[issue["rule_id"]].append(f)
    # 每个 rule 下去重 scenario
    out: dict[str, list[dict]] = {}
    for rule_id, items in grouped.items():
        seen: set[str] = set()
        unique: list[dict] = []
        for item in items:
            sid = item.get("scenario_id", "")
            if sid in seen:
                continue
            seen.add(sid)
            unique.append(item)
        out[rule_id] = unique
    return out


def _issue_body(rule_id: str, scenarios: list[dict], meta: dict, merged_pr: int | None) -> str:
    lines = [
        "## 来源",
        "",
        f"- 报告时间：`{meta.get('generated_at', 'unknown')}`",
        f"- LLM：`{meta.get('llm', 'unknown')}`",
    ]
    if merged_pr:
        lines.append(f"- 触发合并 PR：#{merged_pr}")
    lines.extend(["", "## 问题规则", "", f"`{rule_id}`", ""])

    hints = {i["rule_id"]: i.get("fix_hint", "") for s in scenarios for i in s.get("issues", [])}
    if rule_id in hints and hints[rule_id]:
        lines.extend([f"**修复指引**：{hints[rule_id]}", ""])

    lines.extend(["## 失败场景", ""])
    for s in scenarios:
        lines.append(f"### {s.get('scenario_id')} · {s.get('scenario_name')}")
        lines.append(
            f"- 维度：场景={s.get('scene')} | 背景={s.get('background')} | "
            f"心态={s.get('mindset')} | 情绪={s.get('emotion')} | "
            f"关系={s.get('relationship')} | 时长={s.get('duration')}"
        )
        lines.append(f"- 得分：{s.get('score')}")
        for issue in s.get("issues", []):
            if issue.get("rule_id") != rule_id:
                continue
            turn = issue.get("turn_index")
            turn_s = f"（第 {turn + 1} 轮）" if turn is not None else ""
            lines.append(
                f"  - [{issue.get('severity')}] {issue.get('message')}{turn_s}"
            )
        lines.append("")
        lines.append("<details><summary>对话记录</summary>")
        lines.append("")
        for t in s.get("transcript") or []:
            lines.append(f"**用户**：{t.get('user')}")
            lines.append(f"**NPC**：{t.get('assistant')}")
            lines.append("")
        lines.append("</details>")
        lines.append("")

    lines.extend(
        [
            "## 开发人员",
            "",
            "1. `cd backend && python scripts/run_dialogue_quality.py --scenario <id>` 复现",
            "2. 按 fix_hint 修改后跑全量评测",
            "3. 通过 OpenSpec / 人工 PR 合入（本 Issue 由测试 Automation 创建，不会自动开 PR）",
            "",
            "_由对话质量测试 Automation 自动生成。_",
        ]
    )
    return "\n".join(lines)


def _issue_title(rule_id: str, count: int) -> str:
    return f"[对话质量] {rule_id} · {count} 场景失败"


def _existing_issue_titles() -> set[str]:
    try:
        out = subprocess.run(
            ["gh", "issue", "list", "--label", LABEL, "--state", "open", "--json", "title"],
            capture_output=True,
            text=True,
            check=True,
        )
        items = json.loads(out.stdout or "[]")
        return {i.get("title", "") for i in items}
    except (subprocess.CalledProcessError, FileNotFoundError, json.JSONDecodeError):
        return set()


def main() -> int:
    parser = argparse.ArgumentParser(description="从 latest.json 创建 dialogue-quality GitHub Issues")
    parser.add_argument("--dry-run", action="store_true", help="只打印，不创建 Issue")
    parser.add_argument("--merged-pr", type=int, default=None, help="触发本次测试的已合并 PR 号")
    parser.add_argument(
        "--report",
        type=Path,
        default=REPORT,
        help="报告 JSON 路径",
    )
    args = parser.parse_args()

    meta, failures = _load_failures(args.report)
    if not failures:
        print("无 critical/major 失败，无需创建 Issue。")
        return 0

    grouped = _group_by_rule(failures)
    existing = _existing_issue_titles()
    created = 0

    for rule_id, scenarios in sorted(grouped.items()):
        title = _issue_title(rule_id, len(scenarios))
        if title in existing:
            print(f"跳过（已有 open Issue）：{title}")
            continue
        body = _issue_body(rule_id, scenarios, meta, args.merged_pr)
        if args.dry_run:
            print(f"\n--- DRY RUN Issue ---\nTitle: {title}\n{body[:500]}...\n")
            created += 1
            continue
        try:
            subprocess.run(
                [
                    "gh",
                    "issue",
                    "create",
                    "--title",
                    title,
                    "--body",
                    body,
                    "--label",
                    LABEL,
                ],
                check=True,
            )
            print(f"已创建 Issue：{title}")
            created += 1
        except FileNotFoundError:
            print("未找到 gh CLI，请在 Automation 最终回复中粘贴报告摘要。", file=sys.stderr)
            return 3
        except subprocess.CalledProcessError as e:
            print(f"创建 Issue 失败：{e}", file=sys.stderr)
            return 1

    if args.dry_run:
        print(f"\n预览 {created} 个 Issue（dry-run）。")
    else:
        print(f"共创建 {created} 个 Issue。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
