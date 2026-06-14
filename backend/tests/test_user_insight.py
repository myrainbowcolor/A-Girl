"""用户洞察分析单元测试。"""
import tempfile
import time

import pytest

from app.config import Settings
from app.db import Database
from app.domain import EmotionState, Message, Persona, Relationship, UserMeta
from app.user_insight import (
    UserInsightAnalysis,
    analyze_rules,
    analyze_user,
    compose_proactive_message,
    proactive_reason,
    rule_proactive_message,
)


@pytest.fixture
def db():
    with tempfile.NamedTemporaryFile(suffix=".db") as f:
        d = Database(f.name)
        yield d
        d.close()


def test_analyze_rules_vent_intent():
    meta = UserMeta(user_id="u1", sentiment_ema=-0.4, last_sentiment=-0.5)
    emotion = EmotionState(pleasure=-0.3, arousal=0.2)
    rel = Relationship(affinity=20)
    lines = ["最近好累啊", "工作压力好大", "有点想放弃"]
    r = analyze_rules(lines, meta, emotion, rel)
    assert r.intent == "倾诉/发泄"
    assert r.proactive_need in ("comfort", "follow_up", "none")
    assert r.confidence >= 0.45


def test_analyze_rules_share_celebrate():
    meta = UserMeta(user_id="u1", sentiment_ema=0.4, last_sentiment=0.5)
    emotion = EmotionState(pleasure=0.5, arousal=0.4)
    rel = Relationship(affinity=30)
    lines = ["今天考试通过了！", "太开心了"]
    r = analyze_rules(lines, meta, emotion, rel)
    assert r.intent == "分享喜悦"
    assert r.proactive_need == "celebrate"


def test_analyze_rules_empty():
    meta = UserMeta(user_id="u1")
    r = analyze_rules([], meta, EmotionState(), Relationship())
    assert r.behavior == "正常互动"
    assert r.proactive_need == "none"


def test_analyze_user_without_llm():
    meta = UserMeta(user_id="u1", sentiment_ema=-0.3)
    lines = ["好烦", "不想说话"]
    r = analyze_user(lines, meta, EmotionState(), Relationship(), llm=None, use_llm=False)
    assert isinstance(r, UserInsightAnalysis)
    assert r.intent == "倾诉/发泄"


def test_proactive_reason():
    a = UserInsightAnalysis(state="低落", intent="倾诉/发泄", proactive_need="comfort")
    assert "关怀" in proactive_reason("comfort", a)


def test_rule_proactive_message_templates():
    persona = Persona(name="小语")
    a = UserInsightAnalysis(topic_hint="工作压力", state="低落")
    msg = rule_proactive_message("comfort", a, persona)
    assert len(msg) >= 10
    msg2 = rule_proactive_message("follow_up", a, persona)
    assert "工作压力" in msg2


def test_compose_proactive_message_fallback():
    persona = Persona()
    a = UserInsightAnalysis(topic_hint="测试", proactive_need="reconnect", state="平稳")
    msg = compose_proactive_message("reconnect", a, persona, Relationship(), llm=None)
    assert "小语" in msg or "有一阵子" in msg


def test_db_persists_insight_fields(db):
    meta = UserMeta(
        user_id="u1",
        user_behavior="连发短消息",
        user_intent="倾诉/发泄",
        user_state="低落",
        proactive_topic="工作压力",
        last_insight_at=time.time(),
    )
    db.save_user_meta(meta)
    loaded = db.get_user_meta("u1")
    assert loaded.user_behavior == "连发短消息"
    assert loaded.user_intent == "倾诉/发泄"
    assert loaded.user_state == "低落"
    assert loaded.proactive_topic == "工作压力"


def test_insight_via_chat_history(db):
    db.add_message(Message(session_id="sess-u1", role="user", content="好烦", created_at=time.time()))
    db.add_message(Message(session_id="sess-u1", role="user", content="压力好大", created_at=time.time()))
    meta = UserMeta(user_id="u1", sentiment_ema=-0.35, last_sentiment=-0.4, interaction_count=3)
    db.save_user_meta(meta)
    history = db.recent_messages("sess-u1", 8)
    lines = [m.content for m in history if m.role == "user"]
    r = analyze_rules(lines, meta, EmotionState(), Relationship())
    assert r.intent == "倾诉/发泄"
