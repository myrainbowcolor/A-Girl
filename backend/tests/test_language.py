"""用户输入语言检测与回复语言匹配。"""
import pytest

from app.domain import EmotionState, Persona, Relationship
from app.language import (
    detect_user_language,
    language_instruction,
    reply_language_mismatch,
)
from app.persona import build_system_prompt


def test_detect_chinese():
    assert detect_user_language("你好呀，最近有点累") == "zh"


def test_detect_english():
    assert detect_user_language("I feel really stressed today") == "en"


def test_detect_mixed():
    assert detect_user_language("今天 meeting 好累啊") == "mixed"


def test_prompt_includes_chinese_instruction():
    p = build_system_prompt(
        Persona(), EmotionState(), Relationship(), [], user_text="你好"
    )
    assert "【语言】" in p
    assert "中文" in p
    assert "严格遵循上方【语言】" in p


def test_prompt_includes_english_instruction():
    p = build_system_prompt(
        Persona(), EmotionState(), Relationship(), [], user_text="Hello there"
    )
    assert "English" in p
    assert language_instruction("en") in p


def test_reply_language_mismatch():
    assert reply_language_mismatch("zh", "Hello! How are you doing today?")
    assert not reply_language_mismatch("zh", "你好呀，我在呢")
    assert reply_language_mismatch("en", "你好，我完全理解你的感受")
