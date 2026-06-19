from app.reply_guard import (
    guard_closed_user_reply,
    meta_pushback_ok,
    polish_reply,
    reply_is_companion_ok,
    reply_similarity,
    scene_fallback_reply,
    user_is_closed,
)


def test_user_is_closed():
    assert user_is_closed("不想说")
    assert user_is_closed("..")
    assert not user_is_closed("今天加班好累")
    assert not user_is_closed("随便聊聊")


def test_guard_replaces_pushy_on_closed():
    out = guard_closed_user_reply("不想说", "嗯……你愿意多说一点吗？我听着。")
    assert "愿意多说" not in out
    assert "我陪着" in out or "不说也行" in out


def test_meta_pushback_fallback():
    out = scene_fallback_reply("为啥一定要跟你聊天?")
    assert out
    assert "必须" in out or "强迫" in out or "不用" in out
    assert "小确幸" not in out


def test_identity_fallback():
    out = scene_fallback_reply("你是机器人吗")
    assert out
    assert "AI" in out or "小语" in out


def test_polish_replaces_bad_llm():
    bad = "哈哈，很高兴你和我有相似之处，或许我们可以聊聊小确幸。"
    out = polish_reply("你是机器人吗", bad)
    assert "相似之处" not in out
    assert "小确幸" not in out


def test_polish_avoids_repeat_with_prior():
    prior = "嗯，我陪着。不急着说~"
    out = polish_reply("你真好", prior, prior_reply=prior)
    assert reply_similarity(out, prior) < 0.82
    assert "开心" in out or "高兴" in out or "暖" in out


def test_polish_closed_minimal():
    bad = "嗯，还好，最近工作挺顺利的。你最近忙吗？"
    out = polish_reply("..", bad)
    assert reply_is_companion_ok(out)
    assert "工作" not in out


def test_polish_meta_pushback_not_pushy():
    bad = "嗯，那我们就聊聊天吧。你有没有什么小确幸或者好玩的事儿想分享？"
    out = polish_reply("为啥一定要跟你聊天?", bad)
    assert "小确幸" not in out
    assert "愿意多说" not in out


def test_polish_meta_repeat():
    prior = "不用一定要呀，想聊就聊，不想聊也完全可以。我在这儿，不催你~"
    bad = "我当然可以，不过咱们聊聊天，啥也不必说。"
    out = polish_reply("为啥一定要跟你聊天?", bad, prior_reply=prior)
    assert meta_pushback_ok(out)
    assert "小确幸" not in out
