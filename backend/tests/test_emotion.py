from app.domain import EmotionState, Persona, Relationship, RelationshipStage
from app.emotion import EmotionEngine, analyze_sentiment


def test_sentiment_positive_and_negative():
    assert analyze_sentiment("今天好开心，谢谢你陪我") > 0
    assert analyze_sentiment("我好难过，压力好大想哭") < 0
    assert analyze_sentiment("今天天气一般") == 0.0


def test_positive_input_raises_pleasure():
    engine = EmotionEngine()
    e = EmotionState(pleasure=0.0, arousal=0.0, dominance=0.0)
    new_e, sentiment, _ = engine.appraise(e, "好喜欢你，今天超级开心")
    assert sentiment > 0
    assert new_e.pleasure > e.pleasure


def test_negative_input_lowers_pleasure():
    engine = EmotionEngine()
    e = EmotionState(pleasure=0.5, arousal=0.0, dominance=0.0)
    new_e, sentiment, _ = engine.appraise(e, "我好难过，好孤独，想哭")
    assert sentiment < 0
    assert new_e.pleasure < e.pleasure


def test_relationship_grows_with_positive_interaction():
    engine = EmotionEngine()
    rel = Relationship()
    for _ in range(40):
        rel = engine.update_relationship(rel, 0.8)
    assert rel.affinity > 15
    assert rel.stage in (RelationshipStage.ACQUAINTED, RelationshipStage.FRIEND, RelationshipStage.CLOSE)


def test_emotion_decays_toward_baseline():
    engine = EmotionEngine()
    e = EmotionState(pleasure=0.9, arousal=0.9, dominance=0.0)
    new_e, _, _ = engine.appraise(e, "嗯")  # 中性输入
    assert new_e.pleasure < 0.9
    assert new_e.arousal < 0.9


def test_persona_agreeableness_boosts_empathy():
    engine = EmotionEngine()
    e = EmotionState(pleasure=0.0, arousal=0.0, dominance=0.0)
    low = Persona(agreeableness=0.3)
    high = Persona(agreeableness=0.95)
    _, s_low, _ = engine.appraise(e, "我好难过", persona=low)
    _, s_high, _ = engine.appraise(e, "我好难过", persona=high)
    assert s_low == s_high  # sentiment same
    e2_low, _, _ = engine.appraise(EmotionState(), "我好难过", persona=low)
    e2_high, _, _ = engine.appraise(EmotionState(), "我好难过", persona=high)
    assert e2_high.pleasure < e2_low.pleasure  # 高宜人性共情传导更强
