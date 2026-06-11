"""对话质量失败记录与报告输出。"""
from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

from .runner import ScenarioResult


def _default_report_dir() -> Path:
    return Path(__file__).resolve().parent.parent.parent / "reports" / "dialogue_quality"


class DialogueQualityReporter:
    def __init__(self, report_dir: Path | None = None) -> None:
        self.report_dir = report_dir or _default_report_dir()
        self.report_dir.mkdir(parents=True, exist_ok=True)

    def write_run_report(
        self,
        results: list[ScenarioResult],
        *,
        llm_name: str = "mock",
    ) -> Path:
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        payload = {
            "generated_at": ts,
            "llm": llm_name,
            "summary": self._summary(results),
            "scenarios": [self._scenario_payload(r) for r in results],
            "failures": [self._failure_payload(r) for r in results if r.issues],
        }
        latest = self.report_dir / "latest.json"
        stamped = self.report_dir / f"run_{ts}.json"
        text = json.dumps(payload, ensure_ascii=False, indent=2)
        latest.write_text(text, encoding="utf-8")
        stamped.write_text(text, encoding="utf-8")

        failures_path = self.report_dir / "failures.jsonl"
        with failures_path.open("a", encoding="utf-8") as fh:
            for r in results:
                if not r.issues:
                    continue
                line = json.dumps(self._failure_payload(r), ensure_ascii=False)
                fh.write(line + "\n")

        self._write_markdown(results, llm_name)
        return latest

    def _summary(self, results: list[ScenarioResult]) -> dict:
        total = len(results)
        failed = sum(1 for r in results if r.issues)
        critical = sum(len(r.critical_issues) for r in results)
        major = sum(len(r.major_issues) for r in results)
        avg_score = sum(r.score for r in results) / total if total else 0.0
        return {
            "total_scenarios": total,
            "scenarios_with_issues": failed,
            "critical_issue_count": critical,
            "major_issue_count": major,
            "average_score": round(avg_score, 1),
        }

    @staticmethod
    def _scenario_payload(result: ScenarioResult) -> dict:
        s = result.scenario
        return {
            "id": s.id,
            "name": s.name,
            "scene": s.scene,
            "background": s.background,
            "mindset": s.mindset,
            "emotion": s.emotion,
            "relationship": s.relationship,
            "duration": s.duration,
            "description": s.description,
            "passed": result.passed,
            "score": result.score,
            "issues": [asdict(i) for i in result.issues],
            "turns": [asdict(t) for t in result.turns],
        }

    @staticmethod
    def _failure_payload(result: ScenarioResult) -> dict:
        s = result.scenario
        return {
            "scenario_id": s.id,
            "scenario_name": s.name,
            "scene": s.scene,
            "background": s.background,
            "mindset": s.mindset,
            "emotion": s.emotion,
            "relationship": s.relationship,
            "duration": s.duration,
            "score": result.score,
            "issues": [asdict(i) for i in result.issues],
            "transcript": [
                {"user": t.user_text, "assistant": t.reply, "turn": t.turn_index}
                for t in result.turns
            ],
            "developer_notes": (
                "请对照 issues 中的 rule_id 修复对话编排、提示词或 mock/LLM 回复策略。"
                "修复后重新运行 scripts/run_dialogue_quality.py 验证。"
            ),
        }

    def _write_markdown(self, results: list[ScenarioResult], llm_name: str) -> None:
        lines = [
            "# 对话质量评测报告",
            "",
            f"- LLM：`{llm_name}`",
            f"- 场景数：{len(results)}",
            f"- 有问题场景：{sum(1 for r in results if r.issues)}",
            "",
            "## 需开发人员跟进",
            "",
        ]
        problem_results = [r for r in results if r.issues]
        if not problem_results:
            lines.append("_本次全部场景通过启发式检查。_")
        else:
            for r in problem_results:
                s = r.scenario
                lines.append(f"### {s.id} · {s.name}")
                lines.append(
                    f"- 维度：场景={s.scene} | 背景={s.background} | "
                    f"心态={s.mindset} | 情绪={s.emotion} | "
                    f"关系={s.relationship} | 时长={s.duration}"
                )
                lines.append(f"- 得分：{r.score}")
                for issue in r.issues:
                    turn = f"（第 {issue.turn_index + 1} 轮）" if issue.turn_index is not None else ""
                    lines.append(f"  - [{issue.severity}] `{issue.rule_id}`{turn}: {issue.message}")
                lines.append("")
                lines.append("<details><summary>对话记录</summary>")
                lines.append("")
                for t in r.turns:
                    lines.append(f"**用户**：{t.user_text}")
                    lines.append(f"**NPC**：{t.reply}")
                    lines.append("")
                lines.append("</details>")
                lines.append("")

        (self.report_dir / "latest.md").write_text("\n".join(lines), encoding="utf-8")
