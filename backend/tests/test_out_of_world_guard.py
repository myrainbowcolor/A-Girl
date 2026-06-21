from app.dialogue_compose import compose_contextual_reply
from app.in_world_guard import reply_in_world_ok
from app.out_of_world_guard import (
    compose_out_of_world_reply,
    reply_echoes_real_world_query,
    reply_is_stiff_deflection,
    reply_looks_factual_encyclopedia,
    reply_uses_real_world_cognition,
    user_asks_out_of_world,
)
from app.reply_guard import needs_mock_fallback, polish_reply

_STIFF_PHRASES = (
    "现实里",
    "现实问题",
    "百科资料",
    "查资料写答案",
    "游戏里的陪伴",
    "不是我的活儿",
    "答不上来",
    "不太擅长这类",
)

_REAL_WORLD_TERMS = (
    "法国",
    "巴黎",
    "北京",
    "比特币",
    "Python",
    "百度",
    "窗外",
    "搜资料",
    "交作业",
    "天气预报",
    "首都是",
)


def _assert_in_world_only(text: str) -> None:
    assert text
    assert not any(p in text for p in _STIFF_PHRASES)
    assert not any(p in text for p in _REAL_WORLD_TERMS)
    assert "巴黎" not in text


def test_user_asks_out_of_world_factual():
    assert user_asks_out_of_world("法国首都是哪里？")
    assert user_asks_out_of_world("帮我查一下比特币价格")
    assert user_asks_out_of_world("Python怎么写循环")
    assert user_asks_out_of_world("今天北京多少度")
    assert user_asks_out_of_world("量子力学是什么")
    assert user_asks_out_of_world("帮我写一篇作文")
    assert user_asks_out_of_world("1+1等于几")


def test_user_asks_out_of_world_allows_companion():
    assert not user_asks_out_of_world("今天加班好累")
    assert not user_asks_out_of_world("工作怎么办")
    assert not user_asks_out_of_world("随便聊聊")
    assert not user_asks_out_of_world("我不开心了")
    assert not user_asks_out_of_world("你是什么意思")
    assert not user_asks_out_of_world("爱情是什么")
    assert not user_asks_out_of_world("今天天气不错")
    assert not user_asks_out_of_world("今天天气真好")
    assert not user_asks_out_of_world("你是机器人吗")
    assert not user_asks_out_of_world("帮我写一份辞职信")


def test_compose_deflects_without_real_world_terms():
    out = compose_contextual_reply("法国首都是哪里？", [])
    _assert_in_world_only(out)
    assert any(w in out for w in ("城里", "旧志", "地图", "任务", "难住"))


def test_compose_out_of_world_by_category():
    lookup = compose_out_of_world_reply("帮我查一下比特币价格")
    _assert_in_world_only(lookup)
    assert any(w in lookup for w in ("消息", "情报", "线索", "信使"))

    weather = compose_out_of_world_reply("今天北京天气怎么样")
    _assert_in_world_only(weather)
    assert any(w in weather for w in ("灯影", "风向", "钟塔", "出城"))

    homework = compose_out_of_world_reply("Python怎么写循环")
    _assert_in_world_only(homework)
    assert any(w in homework for w in ("谜题", "解谜", "机关", "公会"))


def test_reply_uses_real_world_cognition():
    assert reply_uses_real_world_cognition("法国的首都是巴黎。")
    assert reply_uses_real_world_cognition("我帮你搜资料吧。")
    assert not reply_uses_real_world_cognition("工作的事确实容易压着人。")
    assert not reply_uses_real_world_cognition("嗯，我陪着。不急着说~")


def test_reply_echoes_real_world_query():
    assert reply_echoes_real_world_query("法国啊我记不清了", "法国首都是哪里？")
    assert not reply_echoes_real_world_query("唔，旧志里没翻到", "法国首都是哪里？")


def test_reply_is_stiff_deflection():
    assert reply_is_stiff_deflection("现实里那些百科资料我搞不太懂啦")
    assert not reply_is_stiff_deflection("唔，旧志里也没翻到～你怎么忽然想起问这个？")


def test_reply_looks_factual_encyclopedia():
    factual = "法国的首都是巴黎，位于欧洲西部，人口约6700万。"
    assert reply_looks_factual_encyclopedia(factual)
    companion = "听起来你今天挺累的，先缓口气吧。"
    assert not reply_looks_factual_encyclopedia(companion)


def test_needs_mock_fallback_blocks_real_world_cognition():
    factual = "法国的首都是巴黎，位于欧洲西部。"
    assert needs_mock_fallback(factual, "法国首都是哪里？")
    echo = "法国啊……我细节记不清了。"
    assert needs_mock_fallback(echo, "法国首都是哪里？")


def test_polish_replaces_factual_llm_slip():
    factual = "法国的首都是巴黎，位于欧洲西部，人口约6700万。"
    out = polish_reply("法国首都是哪里？", factual)
    _assert_in_world_only(out)


def test_reply_in_world_ok_rejects_real_world():
    factual = "法国的首都是巴黎，位于欧洲西部。"
    assert not reply_in_world_ok(factual, "法国首都是哪里？")
