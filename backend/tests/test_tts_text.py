"""TTS 文本清洗测试。"""
from app.voice.tts_text import strip_for_tts


def test_strip_emoji():
    assert strip_for_tts("你好呀😊今天开心吗") == "你好呀今天开心吗"


def test_strip_kaomoji_parens():
    assert strip_for_tts("嗨(´・ω・`)最近怎么样") == "嗨最近怎么样"
    assert "T_T" not in strip_for_tts("抱抱（T_T）")


def test_strip_ascii_emoticon():
    assert strip_for_tts("好的 ^_^") == "好的"
    assert ":)" not in strip_for_tts("嗯 :) 我在听")


def test_keep_normal_chinese():
    assert strip_for_tts("今天加班好累，想找人说说") == "今天加班好累，想找人说说"
