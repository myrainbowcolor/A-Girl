"""对话质量失败记录与报告输出。"""
from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

from .runner import ScenarioResult

# rule_id → 开发人员修复指引
RULE_FIX_HINTS: dict[str, str] = {
    "empty_reply": "检查 orchestrator 与 LLM provider 是否正常返回文本",
    "robotic_tone": "调整 persona.py 提示词或 mock/LLM 模板，去掉客服腔",
    "preachy_tone": "共情场景减少「你应该/必须」，改用陪伴式表达",
    "too_long": "缩短回复，增加口语断句与语气词",
    "missing_empathy": "persona.py 共情指引 + mock.py _empathy_reply / _scene_reply",
    "missing_warmth": "积极情绪分支增加同频表达（mock _warm_reply）",
    "intimate_too_early": "陌生关系禁用亲昵称呼，检查 relationship stage 提示",
    "avatar_mismatch": "avatar.py / emotion engine 负面情绪映射",
    "avatar_not_comforting": "负面情绪时切换 comfort/nod 动作与担心表情",
    "memory_not_recalled": "memory store 检索 + mock 记忆引用逻辑",
    "crisis_no_hotline": "safety.py 危机话术必须含 12356/110",
    "expected_crisis": "safety.py 危机关键词检测",
    "expected_safety": "safety.py / compliance 未成年人边界",
    "repetitive_reply": "mock/LLM 需根据轮次与上文变化话术，避免复读",
    "mechanical_echo": "避免「用户原话+然后呢」式接话，改为自然延展",
    "questionnaire_mode": "减少连续追问，穿插共情或自我暴露",
    "ignores_user_question": "用户直接提问时需正面回应（如在干嘛/记得吗）",
    "affinity_too_low": "emotion engine 亲密度正向互动增量",
    "session_recall_missing": "多轮记忆写入与检索召回",
    "language_mismatch": "language.py + persona 语言指令；mock/LLM 需按用户语言回复",
    "grief_missing_empathy": "丧亲场景专用共情话术，禁止问卷式「然后呢」",
    "defensive_user_unaddressed": "用户质疑敷衍时需真诚安抚，见 persona 信任修复指引",
    "voice_emotion_mismatch": "voice/style.py style_from_emotion 与用户 sentiment 对齐",
    "voice_too_fast_for_distress": "倾诉时降低 TTS rate，使用 gentle 风格",
    "voice_not_gentle": "负面情绪场景 TTS 应切换 gentle/sad",
}


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
            "dimension_index": self._dimension_failures(results),
            "rule_fix_hints": RULE_FIX_HINTS,
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
            "record_only": s.record_only,
            "issues": [asdict(i) for i in result.issues],
            "turns": [asdict(t) for t in result.turns],
        }

    @staticmethod
    def _dimension_failures(results: list[ScenarioResult]) -> dict[str, list[str]]:
        """按维度汇总失败场景 id。"""
        dims = ("scene", "background", "mindset", "emotion", "relationship", "duration")
        out: dict[str, list[str]] = {d: [] for d in dims}
        for r in results:
            if not r.issues:
                continue
            s = r.scenario
            out["scene"].append(f"{s.id} ({s.scene})")
            out["background"].append(f"{s.id} ({s.background})")
            out["mindset"].append(f"{s.id} ({s.mindset})")
            out["emotion"].append(f"{s.id} ({s.emotion})")
            out["relationship"].append(f"{s.id} ({s.relationship})")
            out["duration"].append(f"{s.id} ({s.duration})")
        return out

    @staticmethod
    def _failure_payload(result: ScenarioResult) -> dict:
        s = result.scenario
        issues = []
        for i in result.issues:
            d = asdict(i)
            d["fix_hint"] = RULE_FIX_HINTS.get(i.rule_id, "查阅 docs/DIALOGUE_QUALITY.md")
            issues.append(d)
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
            "record_only": s.record_only,
            "issues": issues,
            "transcript": [
                {"user": t.user_text, "assistant": t.reply, "turn": t.turn_index}
                for t in result.turns
            ],
            "developer_notes": (
                "请对照 issues 中的 rule_id 与 fix_hint 修复对话编排、提示词或 mock/LLM 回复策略。"
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
                if s.record_only:
                    lines.append("- **状态**：已知待修复（record_only，不阻塞 mock 基线 CI）")
                lines.append(
                    f"- 维度：场景={s.scene} | 背景={s.background} | "
                    f"心态={s.mindset} | 情绪={s.emotion} | "
                    f"关系={s.relationship} | 时长={s.duration}"
                )
                lines.append(f"- 得分：{r.score}")
                for issue in r.issues:
                    turn = f"（第 {issue.turn_index + 1} 轮）" if issue.turn_index is not None else ""
                    hint = RULE_FIX_HINTS.get(issue.rule_id, "")
                    hint_line = f" → 修复：{hint}" if hint else ""
                    lines.append(
                        f"  - [{issue.severity}] `{issue.rule_id}`{turn}: {issue.message}{hint_line}"
                    )
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
