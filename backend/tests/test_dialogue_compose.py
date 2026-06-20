from app.dialogue_compose import compose_contextual_reply
from app.in_world_guard import reply_in_world_ok


def test_compose_casual_chat():
    out = compose_contextual_reply("随便聊聊", [])
    assert out
    assert "愿意多说" not in out
    assert "新鲜事" not in out


def test_compose_empty_feeling():
    out = compose_contextual_reply("最近总觉得空空的", [])
    assert out
    assert "空" in out or "陪着" in out


def test_compose_resignation_letter():
    out = compose_contextual_reply("帮我写一份辞职信", [])
    assert out
    assert "文书" in out or "写" in out


def test_in_world_rejects_assistant_english():
    assert not reply_in_world_ok("Hello! How can I assist you today?", "你好")


def test_in_world_accepts_chinese():
    assert reply_in_world_ok("嗨～我是小语。今天想聊点什么？", "hello")
