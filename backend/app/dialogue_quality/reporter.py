"""对话质量失败记录与报告输出。"""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path


@dataclass
class FailureRecord:
  scenario_id: str
  scenario_title: str
  scene: str
  background: str
  mindset: str
  emotion: str
  relationship: str
  duration: str
  turn_index: int
  user_text: str
  reply: str
  failed_checks: list[dict]
  tags: list[str]
  notes: str = ""
  llm_provider: str = "mock"


@dataclass
class QualityReport:
  generated_at: str
  llm_provider: str
  total_scenarios: int
  total_turns: int
  passed_turns: int
  failed_turns: int
  failures: list[FailureRecord] = field(default_factory=list)
  summary_by_owner: dict[str, int] = field(default_factory=dict)

  @property
  def pass_rate(self) -> float:
    if self.total_turns == 0:
      return 1.0
    return self.passed_turns / self.total_turns


def build_summary(failures: list[FailureRecord]) -> dict[str, int]:
  counts: dict[str, int] = {}
  for f in failures:
    for chk in f.failed_checks:
      owner = chk.get("owner_hint", "unknown")
      counts[owner] = counts.get(owner, 0) + 1
  return dict(sorted(counts.items(), key=lambda x: -x[1]))


def write_report(report: QualityReport, path: Path) -> None:
  path.parent.mkdir(parents=True, exist_ok=True)
  payload = {
    "generated_at": report.generated_at,
    "llm_provider": report.llm_provider,
    "total_scenarios": report.total_scenarios,
    "total_turns": report.total_turns,
    "passed_turns": report.passed_turns,
    "failed_turns": report.failed_turns,
    "pass_rate": round(report.pass_rate, 4),
    "summary_by_owner": report.summary_by_owner,
    "failures": [asdict(f) for f in report.failures],
  }
  path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def write_markdown_summary(report: QualityReport, path: Path) -> None:
  """给开发人员阅读的简要 Markdown 摘要。"""
  lines = [
    "# 对话质量测试报告",
    "",
    f"- 生成时间：{report.generated_at}",
    f"- LLM：`{report.llm_provider}`",
    f"- 场景数：{report.total_scenarios}",
    f"- 轮次通过率：{report.passed_turns}/{report.total_turns} "
    f"（{report.pass_rate * 100:.1f}%）",
    "",
  ]
  if report.summary_by_owner:
    lines.append("## 问题归属统计")
    lines.append("")
    for owner, cnt in report.summary_by_owner.items():
      lines.append(f"- `{owner}`：{cnt} 项")
    lines.append("")

  if report.failures:
    lines.append("## 待修复项")
    lines.append("")
    for i, f in enumerate(report.failures, 1):
      lines.append(f"### {i}. [{f.scenario_id}] {f.scenario_title} · 第 {f.turn_index + 1} 轮")
      lines.append("")
      lines.append(
        f"**维度**：场景={f.scene} | 背景={f.background} | 心态={f.mindset} | "
        f"情绪={f.emotion} | 关系={f.relationship} | 时长={f.duration}"
      )
      lines.append("")
      lines.append(f"**用户**：{f.user_text}")
      lines.append("")
      lines.append(f"**回复**：{f.reply}")
      lines.append("")
      for chk in f.failed_checks:
        lines.append(
          f"- ❌ `{chk['name']}`（{chk['severity']}）— {chk['message']} "
          f"→ 建议 `{chk['owner_hint']}` 跟进"
        )
      if f.notes:
        lines.append(f"- 备注：{f.notes}")
      lines.append("")
  else:
    lines.append("全部轮次通过当前启发式规则。")
    lines.append("")

  path.write_text("\n".join(lines), encoding="utf-8")


def utc_now_iso() -> str:
  return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
