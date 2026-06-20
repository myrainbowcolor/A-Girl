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


def test_compose_continuation():
    hist = [
        {"role": "user", "content": "去公园逛了逛"},
        {"role": "assistant", "content": "公园呀，出去走走挺好的。"},
    ]
    out = compose_contextual_reply("后来呢", hist)
    assert out
    assert "后来呢，发生什么了" not in out


def test_compose_wrap_up():
    hist = [
        {"role": "user", "content": "去公园逛了逛"},
        {"role": "assistant", "content": "公园呀，出去走走挺好的。"},
    ]
    out = compose_contextual_reply("没啥了", hist)
    assert out
    assert "愿意多说" not in out


def test_compose_repeat_casual_chat():
    hist = [
        {"role": "user", "content": "随便聊聊"},
        {"role": "assistant", "content": "好呀～今天过得怎么样，有什么想跟我分享的？"},
    ]
    out = compose_contextual_reply("随便聊聊", hist, prior_reply=hist[-1]["content"])
    assert out
    assert out != hist[-1]["content"]


def test_compose_work_topic():
    out = compose_contextual_reply("工作上的事", [])
    assert out
    assert "然后呢" not in out
    assert "我懂" not in out


def test_compose_that_is_all():
    out = compose_contextual_reply("就那样吧", [])
    assert out
    assert "然后呢" not in out


def test_in_world_accepts_chinese():
    assert reply_in_world_ok("嗨～我是小语。今天想聊点什么？", "hello")
