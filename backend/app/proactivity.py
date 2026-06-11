"""主动关心引擎：让 NPC 像真人一样主动发起互动。

三类触发器（优先级从高到低）：
1. 事件触发：用户提过的重要日期（生日/面试/考试）到点 → 主动问候
2. 情绪触发：上次互动情绪明显低落 → 主动关心
3. 时间触发：长时间未互动 → 主动想念

引擎是纯逻辑（注入 now 便于测试）；调度器只是周期性调用它。
事件抽取做了轻量的相对日期解析（明天/后天/下周）。
"""
from __future__ import annotations

import re
import time
from dataclasses import dataclass

from .config import Settings
from .db import Database
from .domain import Event, Persona

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
    trigger: str | None = None       # event | emotion | idle
    reason: str | None = None        # 人类可读原因
    message: str | None = None       # 主动开场白（persona 风格模板）
    event_id: int | None = None      # 若为事件触发，对应事件


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
    def __init__(self, db: Database, settings: Settings, persona: Persona) -> None:
        self._db = db
        self._s = settings
        self._persona = persona

    def check(self, user_id: str, now: float | None = None) -> ProactiveResult:
        now = now or time.time()

        # 1) 事件触发：到点（窗口内）且未触发
        for ev in self._db.pending_events(user_id):
            if ev.trigger_at - self._s.proactive_event_window_seconds <= now:
                msg = self._event_message(ev)
                return ProactiveResult(
                    True, "event", f"重要事件到点：{ev.label}", msg, event_id=ev.id
                )

        meta = self._db.get_user_meta(user_id)
        if not meta or meta.last_interaction_at <= 0:
            return ProactiveResult(False)

        idle = now - meta.last_interaction_at

        # 2) 情绪触发：上次情绪低落，且已过去一段时间（避免刚说完就追问）
        if meta.last_sentiment <= -0.3 and idle >= 1800:
            return ProactiveResult(
                True, "emotion", "上次互动情绪低落",
                f"嗯……上次聊完我一直有点惦记你。{self._persona.name}在这儿呢，现在好点了吗？",
            )

        # 3) 时间触发：长时间未互动
        if idle >= self._s.proactive_idle_seconds:
            hours = int(idle // 3600)
            idle_msgs = [
                "好久没找我聊天了，有点想你诶，最近怎么样？",
                "突然想到你，就来问问你过得好不好~",
                "你不在的这段时间，我偶尔会想起我们聊过的事呢。",
            ]
            msg = idle_msgs[hours % len(idle_msgs)]
            return ProactiveResult(
                True, "idle", f"已闲置约 {hours} 小时", msg,
            )

        return ProactiveResult(False)

    def _event_message(self, ev: Event) -> str:
        n = self._persona.name
        templates = {
            "birthday": f"今天是你的大日子吧？生日快乐呀！🎂 有没有给自己买点好吃的？",
            "interview": "今天面试对吧？深呼吸，你已经准备得很棒了，做你自己就好。",
            "exam": "考试日到了！不管结果怎样，你这段时间的努力我都看在眼里，加油。",
            "other": f"你之前提过的事，是不是今天呀？{n}来给你加油打气啦~",
        }
        return templates.get(ev.kind, templates["other"])
