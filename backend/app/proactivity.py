"""主动关心引擎：让 NPC 像真人一样主动发起互动。

触发器（优先级从高到低）：
1. 事件触发：用户提过的重要日期（生日/面试/考试）到点 → 主动问候
2. 首次来访：尚无对话记录 → 主动问候
3. 洞察触发：基于用户行为/意图/状态分析 → 个性化主动沟通
4. 情绪触发：上次互动情绪明显低落 → 主动关心
5. 时间触发：长时间未互动 → 主动想念

引擎是纯逻辑（注入 now 便于测试）；调度器只是周期性调用它。
事件抽取做了轻量的相对日期解析（明天/后天/下周）。
"""
from __future__ import annotations

import time
from dataclasses import dataclass

from .config import Settings
from .db import Database
from .domain import EmotionState, Event, Persona, Relationship, UserMeta
from .llm.base import LLMProvider
from .user_insight import (
    UserInsightAnalysis,
    analyze_user,
    compose_proactive_message,
    proactive_reason,
)

_DAY = 86400

# 关键词 → 事件类型
_EVENT_KINDS = {
    "生日": "birthday",
    "面试": "interview",
    "考试": "exam",
    "比赛": "other",
    "演出": "other",
    "答辩": "other",
}

# 相对日期 → 偏移秒
_RELATIVE_DATES = {
    "今天": 0,
    "明天": 1 * _DAY,
    "后天": 2 * _DAY,
    "大后天": 3 * _DAY,
    "下周": 7 * _DAY,
}


@dataclass
class ProactiveResult:
    should_reach_out: bool
    trigger: str | None = None       # event | welcome | insight | emotion | idle
    reason: str | None = None        # 人类可读原因
    message: str | None = None       # 主动开场白
    event_id: int | None = None      # 若为事件触发，对应事件
    insight: UserInsightAnalysis | None = None


def extract_events(user_text: str, now: float) -> list[Event]:
    """从用户消息里抽取重要事件（含相对日期）。骨架级规则，可替换为 NER。"""
    events: list[Event] = []
    offset = None
    for word, off in _RELATIVE_DATES.items():
        if word in user_text:
            offset = off
            break
    for kw, kind in _EVENT_KINDS.items():
        if kw in user_text:
            trigger_at = now + (offset if offset is not None else 0)
            events.append(
                Event(user_id="", kind=kind, label=user_text.strip()[:60],
                      trigger_at=trigger_at, created_at=now)
            )
            break
    return events


class ProactivityEngine:
    def __init__(
        self,
        db: Database,
        settings: Settings,
        persona: Persona,
        llm: LLMProvider | None = None,
    ) -> None:
        self._db = db
        self._s = settings
        self._persona = persona
        self._llm = llm

    def check(self, user_id: str, now: float | None = None) -> ProactiveResult:
        now = now or time.time()

        # 1) 事件触发：到点（窗口内）且未触发
        for ev in self._db.pending_events(user_id):
            if ev.trigger_at - self._s.proactive_event_window_seconds <= now:
                msg = self._event_message(ev)
                return ProactiveResult(
                    True, "event", f"重要事件到点：{ev.label}", msg, event_id=ev.id
                )

        # 2) 首次来访：尚无对话记录 → 主动问候
        if not self._db.has_chat_history(user_id):
            name = self._persona.name
            return ProactiveResult(
                True,
                "welcome",
                "首次来访",
                f"嗨，我是{name}～刚上线，有什么想聊的吗？",
            )

        meta = self._db.get_user_meta(user_id)
        if not meta or meta.last_interaction_at <= 0:
            return ProactiveResult(False)

        idle = now - meta.last_interaction_at
        emotion = self._db.get_emotion(user_id) or EmotionState()
        relationship = self._db.get_relationship(user_id) or Relationship()

        # 3) 洞察触发：基于行为/意图/状态分析
        insight_result = self._check_insight(user_id, meta, emotion, relationship, idle, now)
        if insight_result:
            return insight_result

        # 4) 情绪触发：上次情绪低落，且已过去一段时间（避免刚说完就追问）
        if meta.last_sentiment <= -0.3 and idle >= 1800:
            return ProactiveResult(
                True, "emotion", "上次互动情绪低落",
                f"上次聊天时你好像有点低落，后来我时不时还会想起你。"
                f"现在还好吗？"
            )

        # 5) 时间触发：长时间未互动
        if idle >= self._s.proactive_idle_seconds:
            hours = int(idle // 3600)
            return ProactiveResult(
                True, "idle", f"已闲置约 {hours} 小时",
                f"好久没聊了，有点想你～最近还好吗？"
            )

        return ProactiveResult(False)

    def _check_insight(
        self,
        user_id: str,
        meta: UserMeta,
        emotion: EmotionState,
        relationship: Relationship,
        idle: float,
        now: float,
    ) -> ProactiveResult | None:
        if not self._s.proactive_insight_enabled:
            return None
        if idle < self._s.proactive_insight_min_idle_seconds:
            return None
        if meta.last_proactive_at > 0:
            since_proactive = now - meta.last_proactive_at
            if since_proactive < self._s.proactive_insight_cooldown_seconds:
                return None

        session_id = f"sess-{user_id}"
        history = self._db.recent_messages(session_id, self._s.user_insight_history_limit)
        user_lines = [m.content for m in history if m.role == "user"]
        if not user_lines:
            return None

        analysis = analyze_user(
            user_lines,
            meta,
            emotion,
            relationship,
            llm=self._llm if self._s.user_insight_use_llm else None,
            persona=self._persona,
            use_llm=self._s.user_insight_use_llm,
        )
        if analysis.proactive_need == "none":
            return None
        if analysis.confidence < self._s.proactive_insight_min_confidence:
            return None

        need = analysis.proactive_need
        msg = compose_proactive_message(
            need,
            analysis,
            self._persona,
            relationship,
            llm=self._llm if self._s.user_insight_use_llm else None,
            rel_summary=meta.relationship_summary,
        )
        reason = proactive_reason(need, analysis)
        return ProactiveResult(
            True, "insight", reason, msg, insight=analysis
        )

    def _event_message(self, ev: Event) -> str:
        name = self._persona.name
        templates = {
            "birthday": (
                f"今天是你的大日子吧？生日快乐呀！🎂 "
                f"记得给自己留点放松时间，{name} 替你开心～"
            ),
            "interview": (
                "今天是不是有面试呀？深呼吸一下，做你自己就很好。"
                "不管结果怎样，我都替你加油。"
            ),
            "exam": (
                "考试的日子到啦，加油！"
                "尽力就好，结果出来之前先别跟自己较劲，你已经很努力了。"
            ),
            "other": "你之前提过的事，今天是不是到啦？想第一时间来给你鼓鼓劲～",
        }
        return templates.get(ev.kind, templates["other"])
