from app.domain import Persona, Relationship
from app.emotion.analyzer import analyze_lexicon, analyze_text
from app.emotion.relationship_insight import (
    build_insight,
    compute_health_score,
    infer_trend,
)


def test_analyze_lexicon_positive():
    r = analyze_lexicon("今天好开心，谢谢你陪我")
    assert r.sentiment > 0
    assert r.source == "lexicon"


def test_analyze_lexicon_negative():
    r = analyze_lexicon("我好难过，压力好大想哭")
    assert r.sentiment < 0


def test_analyze_lexicon_exam_anxiety():
    r = analyze_lexicon("感觉什么都记不住")
    assert r.sentiment < 0


def test_analyze_lexicon_sick_and_lonely():
    assert analyze_lexicon("我感冒了，头好痛").sentiment < 0
    assert analyze_lexicon("过年一个人，有点落寞").sentiment < 0


def test_analyze_lexicon_bored_is_neutral():
    """无聊闲聊不应触发负面情绪，避免数字人误显示担心脸。"""
    r = analyze_lexicon("好无聊啊")
    assert r.sentiment == 0.0
    assert r.label == "中性"


def test_analyze_lexicon_self_doubt_and_emo():
    assert analyze_lexicon("同学都升职了，就我还原地踏步").sentiment < 0
    assert analyze_lexicon("emo了今天").sentiment < 0
    assert analyze_lexicon("憋在心里好难受").sentiment < 0


def test_analyze_lexicon_breakup_distance_and_tired():
    """失恋/异地/困倦等应触发负面情感，驱动数字人安抚表情。"""
    assert analyze_lexicon("我们分手了").sentiment < 0
    assert analyze_lexicon("困死了，不想起床").sentiment < 0
    assert analyze_lexicon("刚跟他视频完，挂掉电话好空").sentiment < 0
    assert analyze_lexicon("有时候觉得异地恋好难").sentiment < 0
    assert analyze_lexicon("又失眠了，脑子停不下来").sentiment < 0
    assert analyze_lexicon("一直在想项目会不会黄").sentiment < 0
    # 怀旧场景「好难静下来」不含新增词，应保持中性
    assert analyze_lexicon("那时候日子简单，现在好难静下来").sentiment == 0.0


def test_analyze_text_lexicon_mode():
    r = analyze_text("今天天气一般", llm=None, mode="lexicon")
    assert r.sentiment == 0.0


def test_health_score_bounds():
    score = compute_health_score(affinity=50, sentiment_ema=0.5, interaction_count=10)
    assert 0 <= score <= 100


def test_infer_trend_warming():
    assert infer_trend(0.3, 0.2) == "warming"


def test_build_insight_rule_fallback():
    persona = Persona()
    rel = Relationship(affinity=20)
    insight = build_insight(
        None, persona, rel, sentiment_ema=0.1, last_sentiment=0.2,
        interaction_count=3, memories=[], recent_user_lines=["你好"],
        use_llm=False,
    )
    assert insight.summary
    assert insight.health_score > 0
    assert insight.trend in {"warming", "stable", "cooling", "new"}
