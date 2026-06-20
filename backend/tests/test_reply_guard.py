from app.reply_guard import (
    guard_closed_user_reply,
    needs_mock_fallback,
    polish_reply,
    reply_is_filler_heavy,
    reply_is_generic_llm,
    reply_is_generic_mock,
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


def test_needs_mock_fallback_bad_llm():
    bad = "哈哈，很高兴你和我有相似之处，或许我们可以聊聊小确幸。"
    assert needs_mock_fallback(bad, "你是机器人吗")


def test_needs_mock_fallback_self_talk():
    bad = "嗯，还好，最近工作挺顺利的。你最近忙吗？"
    assert needs_mock_fallback(bad, "..")


def test_reply_is_generic_mock():
    assert reply_is_generic_mock("嗯……你愿意多说一点吗？我听着。")
    assert not reply_is_generic_mock("养猫呀！粘人的小家伙最会撒娇了～")


def test_polish_keeps_good_llm():
    good = "听起来你今天加班到挺晚的，辛苦啦。先缓口气，是哪件事最耗你？"
    out = polish_reply("今天加班好累", good)
    assert out == good


def test_polish_fixes_bad_llm():
    bad = "哈哈，很高兴你和我有相似之处，或许我们可以聊聊小确幸。"
    out = polish_reply("你是机器人吗", bad)
    assert "相似之处" not in out
    assert "小确幸" not in out


def test_reply_is_filler_heavy():
    assert reply_is_filler_heavy("嗯……嗯……我理解了。你想聊什么？")
    assert reply_is_filler_heavy("嗯嗯，有什么新鲜事吗？")
    assert not reply_is_filler_heavy("叫我小语就好，很高兴认识你。")


def test_needs_mock_fallback_filler():
    bad = "嗯嗯，有什么新鲜事吗？"
    assert needs_mock_fallback(bad, "能别嗯嗯的回答吗")


def test_polish_filler_complaint():
    bad = "嗯嗯，有什么新鲜事吗？"
    out = polish_reply("能别嗯嗯的回答吗", bad)
    assert not out.startswith("嗯")
    assert "抱歉" in out or "对不起" in out


def test_polish_avoids_exact_repeat():
    prior = "嗯，我陪着。不急着说~"
    out = polish_reply("..", prior, prior_reply=prior)
    assert reply_similarity(out, prior) < 0.88
