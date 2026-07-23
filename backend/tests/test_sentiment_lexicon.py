from app.sentiment_lexicon import (
    contains_keyword,
    is_longing_utterance,
    is_positive_utterance,
    user_complains_bot_reply,
    user_complains_filler_reply,
)


def test_not_positive_when_unhappy():
    assert not is_positive_utterance("我不开心了")
    assert not contains_keyword("我不开心了", "开心")


def test_positive_when_happy():
    assert is_positive_utterance("今天好开心")


def test_bot_reply_complaint():
    msg = "我不开心了,为什么话要去回忆这些事情?你重要的不是应该首先安慰我吗?"
    assert user_complains_bot_reply(msg)


def test_city_false_positive_on_recall_complaint():
    msg = "为什么话要去回忆这些事情"
    assert not is_positive_utterance(msg)


def test_longing_not_positive_utterance():
    assert is_longing_utterance("好久没聊了，有点想你")
    assert not is_positive_utterance("好久没聊了，有点想你")


def test_filler_complaint_not_minimal_ack():
    assert not user_complains_filler_reply("嗯嗯")
    assert not user_complains_filler_reply("嗯")
    assert user_complains_filler_reply("能别嗯嗯的回答吗")
    assert user_complains_filler_reply("太敷衍了")
    assert is_positive_utterance("今天好开心，考试过了！")
