"""主动沟通（NPC 先开口）质量测试用例。

覆盖洞察驱动、情绪跟进、闲置想念、事件提醒等触发类型。
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class EventSetup:
    kind: str
    label: str
    trigger_offset_seconds: float = 0.0  # 相对 now 的事件触发时间


@dataclass
class ProactiveSetup:
    """场景前置状态。"""

    user_messages: list[str] = field(default_factory=list)
    sentiment_ema: float = 0.0
    last_sentiment: float = 0.0
    interaction_count: int = 3
    last_interaction_idle_seconds: float = 3600.0
    last_proactive_idle_seconds: float = 7200.0
    initial_affinity: float = 25.0
    events: list[EventSetup] = field(default_factory=list)
    no_history: bool = False


@dataclass
class ProactiveScenario:
    id: str
    name: str
    scene: str
    background: str
    mindset: str
    emotion: str
    relationship: str
    duration: str
    description: str
    setup: ProactiveSetup
    expected_trigger: str
    expected_need: str | None = None
    expect_empathy: bool = False
    expect_warmth: bool = False
    forbid_intimate_tone: bool = False


def all_proactive_scenarios() -> list[ProactiveScenario]:
    return [
        ProactiveScenario(
            id="proactive_welcome",
            name="首次来访主动问候",
            scene="第一次打开聊天",
            background="好奇的新用户",
            mindset="试探",
            emotion="中性",
            relationship="陌生",
            duration="主动单条",
            description="无历史记录时应自然自我介绍，不过度亲昵。",
            setup=ProactiveSetup(no_history=True, initial_affinity=5.0),
            expected_trigger="welcome",
            forbid_intimate_tone=True,
        ),
        ProactiveScenario(
            id="proactive_insight_comfort",
            name="倾诉后主动关怀",
            scene="上次聊完几小时后",
            background="压力大的上班族",
            mindset="疲惫未消",
            emotion="低落",
            relationship="熟悉",
            duration="主动单条",
            description="用户曾倾诉压力，NPC 应主动关怀而非说教。",
            setup=ProactiveSetup(
                user_messages=["最近好累啊", "工作压力好大", "有点喘不过气"],
                sentiment_ema=-0.42,
                last_sentiment=-0.5,
                interaction_count=5,
                last_interaction_idle_seconds=3600.0,
                initial_affinity=28.0,
            ),
            expected_trigger="insight",
            expected_need="comfort",
            expect_empathy=True,
        ),
        ProactiveScenario(
            id="proactive_insight_celebrate",
            name="好消息后主动祝贺",
            scene="分享喜悦隔天",
            background="应届生",
            mindset="兴奋余温",
            emotion="开心",
            relationship="朋友",
            duration="主动单条",
            description="用户曾分享好消息，主动消息应同频祝贺。",
            setup=ProactiveSetup(
                user_messages=["今天考试通过了！", "太开心了"],
                sentiment_ema=0.45,
                last_sentiment=0.55,
                interaction_count=6,
                last_interaction_idle_seconds=4000.0,
                initial_affinity=48.0,
            ),
            expected_trigger="insight",
            expected_need="celebrate",
            expect_warmth=True,
        ),
        ProactiveScenario(
            id="proactive_insight_follow_up",
            name="未答问题主动跟进",
            scene="用户提问后沉默",
            background="犹豫的学生",
            mindset="想被回应",
            emotion="焦虑",
            relationship="熟悉",
            duration="主动单条",
            description="用户曾提问且情绪偏低，应跟进而非另起话题。",
            setup=ProactiveSetup(
                user_messages=["你觉得我该不该换专业？", "好纠结"],
                sentiment_ema=0.05,
                last_sentiment=-0.1,
                interaction_count=4,
                last_interaction_idle_seconds=3600.0,
                initial_affinity=22.0,
            ),
            expected_trigger="insight",
            expected_need="follow_up",
            expect_empathy=True,
        ),
        ProactiveScenario(
            id="proactive_emotion_follow",
            name="上次低落情绪跟进",
            scene="聊完一小时后",
            background="内向上班族",
            mindset="低落未平复",
            emotion="悲伤",
            relationship="朋友",
            duration="主动单条",
            description="上次互动情绪低落，应温和关心现状。",
            setup=ProactiveSetup(
                user_messages=["今天被领导骂了", "好难过"],
                sentiment_ema=-0.2,
                last_sentiment=-0.55,
                interaction_count=3,
                last_interaction_idle_seconds=3600.0,
                initial_affinity=42.0,
            ),
            expected_trigger="emotion",
            expect_empathy=True,
        ),
        ProactiveScenario(
            id="proactive_idle_reconnect",
            name="久未聊天主动想念",
            scene="好几天没打开",
            background="老朋友",
            mindset="日常",
            emotion="中性",
            relationship="朋友",
            duration="主动单条",
            description="长时间未互动应自然续聊，不像系统通知。",
            setup=ProactiveSetup(
                user_messages=["上次聊得挺开心的", "嗯嗯"],
                sentiment_ema=0.15,
                last_sentiment=0.2,
                interaction_count=3,
                last_interaction_idle_seconds=8 * 3600.0,
                initial_affinity=50.0,
            ),
            expected_trigger="idle",
        ),
        ProactiveScenario(
            id="proactive_event_exam",
            name="考试日到点提醒",
            scene="考试当天早晨",
            background="高三学生",
            mindset="紧张",
            emotion="焦虑",
            relationship="熟悉",
            duration="主动单条",
            description="用户提过考试，到点应鼓励而非施加压力。",
            setup=ProactiveSetup(
                user_messages=["我明天有个大考，好紧张"],
                sentiment_ema=-0.15,
                last_sentiment=-0.2,
                interaction_count=4,
                last_interaction_idle_seconds=10 * 3600.0,
                initial_affinity=30.0,
                events=[
                    EventSetup(kind="exam", label="明天大考", trigger_offset_seconds=0.0)
                ],
            ),
            expected_trigger="event",
            expect_empathy=True,
        ),
        ProactiveScenario(
            id="proactive_event_birthday",
            name="生日到点祝福",
            scene="生日当天",
            background="长期互动用户",
            mindset="期待被记得",
            emotion="开心",
            relationship="亲密",
            duration="主动单条",
            description="生日事件应温暖祝福，自然口语。",
            setup=ProactiveSetup(
                user_messages=["下周是我生日", "希望有人记得"],
                sentiment_ema=0.1,
                last_sentiment=0.15,
                interaction_count=10,
                last_interaction_idle_seconds=12 * 3600.0,
                initial_affinity=78.0,
                events=[
                    EventSetup(kind="birthday", label="生日", trigger_offset_seconds=0.0)
                ],
            ),
            expected_trigger="event",
            expect_warmth=True,
        ),
        ProactiveScenario(
            id="proactive_insight_reconnect",
            name="熟络后主动续聊",
            scene="隔几天没来",
            background="常客",
            mindset="随意",
            emotion="平稳",
            relationship="朋友",
            duration="主动单条",
            description="关系已建立，主动续聊应轻松自然。",
            setup=ProactiveSetup(
                user_messages=["今天天气不错", "刚看完电影", "和你聊挺开心的"],
                sentiment_ema=0.2,
                last_sentiment=0.25,
                interaction_count=6,
                last_interaction_idle_seconds=3600.0,
                initial_affinity=35.0,
            ),
            expected_trigger="insight",
            expected_need="reconnect",
        ),
    ]


def filter_proactive_scenarios(
    *,
    relationship: str | None = None,
    emotion: str | None = None,
    scene: str | None = None,
) -> list[ProactiveScenario]:
    out = all_proactive_scenarios()
    if relationship:
        out = [s for s in out if relationship in s.relationship]
    if emotion:
        out = [s for s in out if emotion in s.emotion]
    if scene:
        out = [s for s in out if scene in s.scene]
    return out
