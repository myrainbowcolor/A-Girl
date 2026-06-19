from app.reply_guard import guard_closed_user_reply, user_is_closed


def test_user_is_closed():
    assert user_is_closed("不想说")
    assert user_is_closed("..")
    assert not user_is_closed("今天加班好累")


def test_guard_replaces_pushy_on_closed():
    out = guard_closed_user_reply("不想说", "嗯……你愿意多说一点吗？我听着。")
    assert "愿意多说" not in out
    assert "不说也行" in out
