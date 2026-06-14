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
    analyze_speaking_style,
    analyze_thought_pattern,
    analyze_user,
    apply_cumulative_merge,
    build_profile_summary,
    compose_proactive_message,
    meta_to_insight_dict,
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
    meta = UserMeta(user_id="u1", sentiment_ema=-0.4, last_sentiment=-0.5, interaction_count=4)
    emotion = EmotionState(pleasure=-0.3, arousal=0.2)
    rel = Relationship(affinity=20)
    lines = ["最近好累啊", "工作压力好大", "有点想放弃", "烦死了"]
    r = analyze_rules(lines, meta, emotion, rel)
    assert r.intent == "倾诉/发泄"
    assert r.proactive_need in ("comfort", "follow_up", "none")
    assert r.speaking_style != "尚不明确"
    assert r.thought_pattern == "先感受后道理，需要被接住"
    assert r.confidence >= 0.5


def test_analyze_rules_share_celebrate():
    meta = UserMeta(user_id="u1", sentiment_ema=0.4, last_sentiment=0.5, interaction_count=3)
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


def test_speaking_style_short_messages():
    lines = ["嗯", "好", "行吧", "知道了"]
    style = analyze_speaking_style(lines)
    assert "短句" in style


def test_speaking_style_long_messages():
    lines = [
        "我今天想跟你聊聊工作上的事情，最近项目压力特别大，"
        "老板总是改需求，我觉得有点扛不住了。",
        "而且同事之间也有一些摩擦，我不知道该怎么处理。",
    ]
    style = analyze_speaking_style(lines)
    assert "长段" in style or "有条理" in style


def test_thought_pattern_rational():
    meta = UserMeta(user_id="u1", sentiment_ema=0.0)
    lines = ["因为项目延期，所以老板不太高兴", "我觉得应该先分析原因", "如果再这样可能得换团队"]
    pattern = analyze_thought_pattern(lines, meta)
    assert "理性" in pattern or "因果" in pattern


def test_thought_pattern_validation():
    meta = UserMeta(user_id="u1")
    lines = ["你觉得我这样正常吗", "是不是我太敏感了", "你怎么看"]
    pattern = analyze_thought_pattern(lines, meta)
    assert "确认" in pattern or "看法" in pattern


def test_build_profile_summary():
    summary = build_profile_summary(
        "近期互动较活跃",
        "短句为主、表达简练",
        "先感受后道理，需要被接住",
        "倾诉/发泄",
        "低落，需要被看见",
        message_count=5,
        interaction_count=4,
    )
    assert "说话" in summary
    assert "思维" in summary
    assert summary.endswith("。")


def test_apply_cumulative_merge_keeps_specific():
    meta = UserMeta(
        user_id="u1",
        user_speaking_style="短句为主、表达简练",
        user_thought_pattern="先感受后道理，需要被接住",
        user_behavior="近期互动较活跃",
    )
    fresh = UserInsightAnalysis(
        behavior="正常互动",
        speaking_style="尚不明确",
        thought_pattern="尚不明确",
    )
    merged = apply_cumulative_merge(fresh, meta)
    assert merged.speaking_style == "短句为主、表达简练"
    assert merged.thought_pattern == "先感受后道理，需要被接住"
    assert merged.behavior == "近期互动较活跃"


def test_analyze_user_without_llm():
    meta = UserMeta(user_id="u1", sentiment_ema=-0.3, interaction_count=3)
    lines = ["好烦", "不想说话", "压力好大"]
    r = analyze_user(lines, meta, EmotionState(), Relationship(), llm=None, use_llm=False)
    assert isinstance(r, UserInsightAnalysis)
    assert r.intent == "倾诉/发泄"


def test_multi_turn_deepening():
    meta = UserMeta(user_id="u1", interaction_count=8, sentiment_ema=-0.1)
    lines = [
        "嗨", "嗯", "还行",
        "最近有点烦", "工作上的事",
        "老板总是改需求让我很难受，我已经尽量配合了但还是觉得委屈",
        "你觉得我是不是太敏感了",
    ]
    r = analyze_rules(lines, meta, EmotionState(), Relationship(affinity=25))
    assert r.speaking_style != "尚不明确"
    assert r.thought_pattern != "尚不明确"
    assert r.profile_summary != ""
    assert "正常互动" not in r.profile_summary or "互动" in r.profile_summary


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


def test_meta_to_insight_dict():
    assert meta_to_insight_dict(UserMeta(user_id="u1")) is None
    meta = UserMeta(
        user_id="u1",
        user_behavior="互动较活跃",
        user_intent="倾诉/发泄",
        user_state="低落",
        user_speaking_style="短句为主",
        user_thought_pattern="情绪优先",
        user_profile_summary="说话短句为主；思维情绪优先。",
        last_insight_at=1.0,
    )
    d = meta_to_insight_dict(meta)
    assert d["behavior"] == "互动较活跃"
    assert d["speaking_style"] == "短句为主"
    assert d["thought_pattern"] == "情绪优先"
    assert "profile_summary" in d


def test_db_persists_insight_fields(db):
    meta = UserMeta(
        user_id="u1",
        user_behavior="连发短消息",
        user_intent="倾诉/发泄",
        user_state="低落",
        user_speaking_style="短句为主",
        user_thought_pattern="情绪优先",
        user_profile_summary="综合画像测试。",
        proactive_topic="工作压力",
        insight_turn_count=3,
        last_insight_at=time.time(),
    )
    db.save_user_meta(meta)
    loaded = db.get_user_meta("u1")
    assert loaded.user_behavior == "连发短消息"
    assert loaded.user_speaking_style == "短句为主"
    assert loaded.user_thought_pattern == "情绪优先"
    assert loaded.user_profile_summary == "综合画像测试。"
    assert loaded.insight_turn_count == 3


def test_insight_via_chat_history(db):
    db.add_message(Message(session_id="sess-u1", role="user", content="好烦", created_at=time.time()))
    db.add_message(Message(session_id="sess-u1", role="user", content="压力好大", created_at=time.time()))
    meta = UserMeta(user_id="u1", sentiment_ema=-0.35, last_sentiment=-0.4, interaction_count=3)
    db.save_user_meta(meta)
    history = db.recent_messages("sess-u1", 40)
    lines = [m.content for m in history if m.role == "user"]
    r = analyze_rules(lines, meta, EmotionState(), Relationship())
    assert r.intent == "倾诉/发泄"
