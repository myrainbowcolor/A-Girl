from app.dialogue_compose import compose_contextual_reply
from app.in_world_guard import reply_in_world_ok
from app.out_of_world_guard import (
    reply_looks_factual_encyclopedia,
    user_asks_out_of_world,
)
from app.reply_guard import needs_mock_fallback, polish_reply


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


def test_compose_deflects_out_of_world():
    out = compose_contextual_reply("法国首都是哪里？", [])
    assert out
    assert "首都" not in out
    assert "巴黎" not in out
    assert "陪伴" in out or "答不上" in out or "擅长" in out


def test_reply_looks_factual_encyclopedia():
    factual = "法国的首都是巴黎，位于欧洲西部，人口约6700万。"
    assert reply_looks_factual_encyclopedia(factual)
    companion = "听起来你今天挺累的，先缓口气吧。"
    assert not reply_looks_factual_encyclopedia(companion)


def test_needs_mock_fallback_blocks_factual_answer():
    factual = "法国的首都是巴黎，位于欧洲西部。"
    assert needs_mock_fallback(factual, "法国首都是哪里？")


def test_polish_replaces_factual_llm_slip():
    factual = "法国的首都是巴黎，位于欧洲西部，人口约6700万。"
    out = polish_reply("法国首都是哪里？", factual)
    assert "巴黎" not in out
    assert "首都" not in out or "答不上" in out or "陪伴" in out


def test_reply_in_world_ok_rejects_factual():
    factual = "法国的首都是巴黎，位于欧洲西部。"
    assert not reply_in_world_ok(factual, "法国首都是哪里？")
