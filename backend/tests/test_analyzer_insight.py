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
