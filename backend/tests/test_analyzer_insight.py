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


def test_analyze_lexicon_bored_social_smalltalk_warm():
    """无聊摸鱼/社交探问应温和正向，驱动微笑 avatar；勿入负面词典。"""
    r = analyze_lexicon("好无聊啊")
    assert 0.35 <= r.sentiment <= 0.45
    assert "闲聊" in r.label
    r2 = analyze_lexicon("你在干嘛")
    assert 0.35 <= r2.sentiment <= 0.45
    assert "闲聊" in r2.label
    assert analyze_lexicon("好无聊，心情还是很差").sentiment < 0.35
    assert analyze_lexicon("嗯").sentiment == 0.0


def test_analyze_lexicon_longing_warm_not_cheer():
    """想念句温和正向，区别于纯开心报喜。"""
    r = analyze_lexicon("好久没聊了，有点想你")
    assert 0.35 <= r.sentiment <= 0.45
    assert "想念" in r.label


def test_analyze_lexicon_minimal_short_replies():
    """整句极简口语应偏负向，驱动 avatar comfort；长句不误判。"""
    assert analyze_lexicon("还好").sentiment < -0.2
    assert analyze_lexicon("还行").sentiment < -0.2
    assert analyze_lexicon("一般").sentiment < -0.2
    assert analyze_lexicon("不知道").sentiment < -0.2
    assert analyze_lexicon("说不清").sentiment < -0.2
    assert analyze_lexicon("说不上").sentiment < -0.2
    assert analyze_lexicon("我不知道该怎么办").sentiment == 0.0
    assert analyze_lexicon("今天天气一般").sentiment == 0.0


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
    # 怀旧场景「好难静下来」不含新增词，应保持中性
    assert analyze_lexicon("那时候日子简单，现在好难静下来").sentiment == 0.0


def test_analyze_lexicon_anger_defense_parent_insomnia():
    """愤怒/防御/育儿焦虑/失眠反刍等应触发负面情感与安抚表情。"""
    assert analyze_lexicon("老板今天当众骂我，气死了！").sentiment < 0
    assert analyze_lexicon("真想立刻辞职不干了").sentiment < 0
    assert analyze_lexicon("你不懂的，没人懂").sentiment < 0
    assert analyze_lexicon("孩子这次考得不好，我是不是太严厉了").sentiment < 0
    assert analyze_lexicon("我很怕耽误他").sentiment < 0
    assert analyze_lexicon("一直在想项目会不会黄").sentiment < 0
    assert analyze_lexicon("跟对象吵架了，现在谁也不理谁").sentiment < 0
    assert analyze_lexicon("我又乱花钱了，买了根本用不上的东西").sentiment < 0
    assert analyze_lexicon("算了，不想说了").sentiment < 0


def test_analyze_lexicon_positive_offer():
    assert analyze_lexicon("我拿到 dream offer 了！！").sentiment > 0


def test_analyze_lexicon_morning_greeting_warm():
    r = analyze_lexicon("早呀，今天又要上班了")
    assert 0.35 <= r.sentiment <= 0.45
    assert "寒暄" in r.label
    assert analyze_lexicon("困死了，不想起床").sentiment < -0.2
    assert analyze_lexicon("今天要开会").sentiment == 0.0


def test_analyze_lexicon_casual_positive_smalltalk():
    """轻松正向闲聊应温和正向，驱动微笑 avatar。"""
    r = analyze_lexicon("今天天气不错")
    assert 0.35 <= r.sentiment <= 0.45
    assert "闲聊" in r.label
    r2 = analyze_lexicon("刚看完一部挺好的电影")
    assert 0.35 <= r2.sentiment <= 0.45
    assert "闲聊" in r2.label
    assert analyze_lexicon("天气不错但心情还是很差").sentiment < 0.35
    assert analyze_lexicon("今天要开会").sentiment == 0.0


def test_analyze_lexicon_nostalgic_and_pet_warm():
    """怀旧感怀、分享粘人宠物应触发柔和正向，驱动微笑表情。"""
    assert analyze_lexicon("突然想到小时候外婆做的汤圆，好怀念").sentiment > 0
    assert analyze_lexicon("我养了一只叫橘子的猫，超粘人").sentiment > 0
    # 怀旧第二句仍保持中性（勿把「好难」单字入负面）
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
