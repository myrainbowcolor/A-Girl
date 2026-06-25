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


def test_compose_open_avoids_recent():
    from app.dialogue_compose import compose_open_reply

    avoid = ["我听到了。是最近这事一直压着你吗？"]
    out = compose_open_reply("嗯", [], avoid=avoid)
    assert out not in avoid
    assert "一直压着你" not in out


def test_in_world_accepts_chinese():
    assert reply_in_world_ok("嗨～我是小语。今天想聊点什么？", "hello")


def test_compose_morning_commute_not_work_vent():
    out = compose_contextual_reply("早呀，今天又要上班了", [])
    assert out
    assert "不公平" not in out
    assert "忙不过来" not in out
    assert any(w in out for w in ("早", "开工", "上班", "通勤", "鼓劲"))


def test_compose_work_vent_still_routes():
    out = compose_contextual_reply("上班好累", [])
    assert out
    assert any(w in out for w in ("累", "辛苦", "耗", "吐槽", "委屈", "工作"))


def test_compose_insomnia_rumination_followup():
    """失眠反刍续聊应接住清醒/烦躁感，而非通用问卷式「突然还是一阵子」。"""
    hist = [
        {"role": "user", "content": "又失眠了，脑子停不下来"},
        {"role": "assistant", "content": "失眠的时候脑子特别吵，我懂这种难受。"},
        {"role": "user", "content": "一直在想项目会不会黄"},
        {"role": "assistant", "content": "项目悬着的时候最折磨人，我理解你躺不住。"},
    ]
    out = compose_contextual_reply("越躺越清醒，好烦", hist)
    assert out
    assert any(w in out for w in ("清醒", "折磨", "失眠", "睡不着", "脑子"))
    assert "突然" not in out
    assert "一阵子" not in out


def test_compose_lonely_insomnia():
    """孤独+失眠复合句应先接住孤独感，而非纯失眠反刍话术。"""
    out = compose_contextual_reply("凌晨了还睡不着，有点孤独", [])
    assert out
    assert any(w in out for w in ("孤独", "孤单", "寂寞", "难熬"))
    assert "脑子特别吵" not in out
    assert "是什么事在转" not in out


def test_compose_pet_antics_followup():
    """宠物续聊应接住捣蛋细节，而非泛化「发生什么好事啦」报喜句。"""
    hist = [
        {"role": "user", "content": "我养了一只叫橘子的猫，超粘人"},
        {"role": "assistant", "content": "养猫呀！粘人的小家伙最会撒娇了～"},
    ]
    out = compose_contextual_reply("它今天又把杯子打翻了哈哈", hist)
    assert out
    assert "橘子" in out
    assert any(w in out for w in ("打翻", "杯子", "捣蛋", "搞破坏"))
    assert "发生什么好事啦" not in out


def test_compose_minimal_fatigue():
    """单字「累」应返回疲惫共情短句，而非泛化「不太好受」套话。"""
    out = compose_contextual_reply("累", [])
    assert out
    assert any(w in out for w in ("累", "辛苦", "歇", "心疼"))
    assert "不太好受" not in out
