from app.dialogue_compose import compose_contextual_reply
from app.in_world_guard import reply_in_world_ok
from app.out_of_world_guard import (
    compose_out_of_world_reply,
    reply_is_stiff_deflection,
    reply_looks_factual_encyclopedia,
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


def _assert_soft_deflection(text: str) -> None:
    assert text
    assert not any(p in text for p in _STIFF_PHRASES)
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


def test_compose_deflects_out_of_world_softly():
    out = compose_contextual_reply("法国首都是哪里？", [])
    _assert_soft_deflection(out)
    assert "法国" in out or "清楚" in out or "问住" in out


def test_compose_out_of_world_by_category():
    lookup = compose_out_of_world_reply("帮我查一下比特币价格")
    _assert_soft_deflection(lookup)
    assert "查" in lookup or "找" in lookup

    weather = compose_out_of_world_reply("今天北京天气怎么样")
    _assert_soft_deflection(weather)
    assert "温度" in weather or "窗外" in weather or "天气" in weather

    homework = compose_out_of_world_reply("Python怎么写循环")
    _assert_soft_deflection(homework)


def test_reply_is_stiff_deflection():
    assert reply_is_stiff_deflection("现实里那些百科资料我搞不太懂啦")
    assert not reply_is_stiff_deflection("法国啊……我细节记不清了。你怎么忽然想到问这个？")


def test_reply_looks_factual_encyclopedia():
    factual = "法国的首都是巴黎，位于欧洲西部，人口约6700万。"
    assert reply_looks_factual_encyclopedia(factual)
    companion = "听起来你今天挺累的，先缓口气吧。"
    assert not reply_looks_factual_encyclopedia(companion)


def test_needs_mock_fallback_blocks_factual_and_stiff():
    factual = "法国的首都是巴黎，位于欧洲西部。"
    assert needs_mock_fallback(factual, "法国首都是哪里？")
    stiff = "我是游戏里的陪伴者，查资料写答案不是我的活儿。"
    assert needs_mock_fallback(stiff, "法国首都是哪里？")


def test_polish_replaces_factual_llm_slip():
    factual = "法国的首都是巴黎，位于欧洲西部，人口约6700万。"
    out = polish_reply("法国首都是哪里？", factual)
    _assert_soft_deflection(out)


def test_reply_in_world_ok_rejects_factual():
    factual = "法国的首都是巴黎，位于欧洲西部。"
    assert not reply_in_world_ok(factual, "法国首都是哪里？")
